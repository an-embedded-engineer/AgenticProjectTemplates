using System.Diagnostics;
using System.Text.RegularExpressions;

namespace AgentCliTmux;

internal static partial class Program
{
    private static readonly HashSet<string> AgentChoices = ["codex", "claude", "copilot"];
    private static readonly HashSet<string> ModeChoices = ["start", "continue"];
    private static readonly HashSet<string> ShellCommands = ["bash", "fish", "sh", "zsh"];

    public static int Main(string[] args)
    {
        try
        {
            return Run(args);
        }
        catch (CliException e)
        {
            Console.Error.WriteLine($"error: {e.Message}");
            return 2;
        }
        catch (Exception e)
        {
            Console.Error.WriteLine($"error: {e.Message}");
            return 2;
        }
    }

    private static int Run(string[] args)
    {
        if (args.Length == 0)
        {
            throw new CliException("command is required");
        }

        var command = args[0];
        // 外部 CLI パーサー依存を避け、テンプレート単体で build/run できるよう最小パーサーにしている。
        var options = ParseOptions(args[1..]);
        var runner = new TmuxRunner(options.ContainsKey("dry-run"));
        var builder = new AgentCommandBuilder();

        return command switch
        {
            "start" => StartAgent(options, runner, builder, allowExistingInactive: false),
            "ensure" => StartAgent(options, runner, builder, allowExistingInactive: true),
            "send-prompt" => SendPrompt(options, runner),
            "capture" => CapturePane(options, runner),
            "status" => ShowStatus(options, runner),
            "stop" => StopAgent(options, runner, builder),
            "sleep" => SleepOnly(options, runner),
            _ => throw new CliException($"Unsupported command: {command}"),
        };
    }

    private static int StartAgent(
        Dictionary<string, string?> options,
        TmuxRunner runner,
        AgentCommandBuilder builder,
        bool allowExistingInactive)
    {
        var target = ParseTarget(options);
        var cwd = ResolveCwd(Require(options, "cwd"));
        var agent = RequireChoice(options, "agent", AgentChoices);
        var mode = options.TryGetValue("mode", out var modeValue) && modeValue is not null
            ? RequireChoice(options, "mode", ModeChoices)
            : allowExistingInactive ? builder.DefaultModeForEnsure(agent) : "start";
        var model = options.GetValueOrDefault("model");
        var (cols, rows) = ParseSize(options.GetValueOrDefault("size") ?? "220x60");
        var split = options.GetValueOrDefault("split") ?? "horizontal";
        var splitFrom = options.GetValueOrDefault("split-from");

        if (runner.DryRun)
        {
            var command = builder.Build(new AgentCommandSpec(agent, mode, model, cwd));
            if (target.Pane == "0.0")
            {
                runner.NewSession(target, cwd, cols, rows);
            }
            else
            {
                runner.SplitWindow(target, cwd, split, splitFrom);
            }

            runner.SendKeys(target, command, "Enter");
            return 0;
        }

        if (!runner.HasSession(target))
        {
            if (target.Pane != "0.0")
            {
                throw new CliException("Cannot create a new session for non-0.0 pane");
            }

            runner.NewSession(target, cwd, cols, rows);
            mode = options.GetValueOrDefault("mode") ?? "start";
        }
        else if (runner.HasPane(target))
        {
            if (!allowExistingInactive)
            {
                throw new CliException($"Target pane already exists: {target.Value}");
            }

            var process = runner.CurrentProcess(target)
                ?? throw new CliException($"Cannot determine current process: {target.Value}");
            if (!process.IsShell)
            {
                Console.WriteLine($"Agent process already appears active: {process.Command}");
                return 0;
            }

            mode = options.GetValueOrDefault("mode") ?? builder.DefaultModeForEnsure(agent);
        }
        else
        {
            runner.SplitWindow(target, cwd, split, splitFrom);
            if (!runner.HasPane(target))
            {
                throw new CliException($"Split did not create requested pane: {target.Value}");
            }

            mode = options.GetValueOrDefault("mode") ?? "start";
        }

        runner.SendKeys(target, builder.Build(new AgentCommandSpec(agent, mode, model, cwd)), "Enter");
        return 0;
    }

    private static int SendPrompt(Dictionary<string, string?> options, TmuxRunner runner)
    {
        var target = ParseTarget(options);
        var promptFile = Path.GetFullPath(Require(options, "file"));

        if (!runner.DryRun && !File.Exists(promptFile))
        {
            throw new CliException($"--file must be an existing file: {promptFile}");
        }

        if (!runner.DryRun && (!runner.HasSession(target) || !runner.HasPane(target)))
        {
            throw new CliException($"Target pane does not exist: {target.Value}");
        }

        runner.LoadAndPaste(target, promptFile);

        var submitDelay = ParseSleepSeconds(options.GetValueOrDefault("submit-delay") ?? "0");
        if (submitDelay > 0)
        {
            runner.Sleep(submitDelay);
        }

        runner.SendKeys(target, "Enter");

        var sleepAfter = ParseSleepSeconds(options.GetValueOrDefault("sleep-after") ?? "0");
        if (sleepAfter > 0)
        {
            runner.Sleep(sleepAfter);
        }

        if (options.ContainsKey("capture-after-sleep"))
        {
            var result = runner.Capture(target, ParseInt(options.GetValueOrDefault("lines") ?? "120", "--lines"));
            if (result.ReturnCode != 0)
            {
                Console.Error.Write(result.Stderr);
                return result.ReturnCode;
            }

            Console.Write(result.Stdout);
        }

        return 0;
    }

    private static int CapturePane(Dictionary<string, string?> options, TmuxRunner runner)
    {
        var target = ParseTarget(options);
        var sleepBefore = ParseSleepSeconds(options.GetValueOrDefault("sleep-before") ?? "0");
        if (sleepBefore > 0)
        {
            runner.Sleep(sleepBefore);
        }

        if (!runner.HasSession(target) || !runner.HasPane(target))
        {
            throw new CliException($"Target pane does not exist: {target.Value}");
        }

        var result = runner.Capture(target, ParseInt(options.GetValueOrDefault("lines") ?? "120", "--lines"));
        if (result.ReturnCode != 0)
        {
            Console.Error.Write(result.Stderr);
            return result.ReturnCode;
        }

        Console.Write(result.Stdout);
        return 0;
    }

    private static int ShowStatus(Dictionary<string, string?> options, TmuxRunner runner)
    {
        var target = ParseTarget(options);
        var sleepBefore = ParseSleepSeconds(options.GetValueOrDefault("sleep-before") ?? "0");
        if (sleepBefore > 0)
        {
            runner.Sleep(sleepBefore);
        }

        var sessionExists = runner.HasSession(target);
        var paneExists = sessionExists && runner.HasPane(target);
        Console.WriteLine($"session: {target.Session}");
        Console.WriteLine($"session_exists: {sessionExists.ToString().ToLowerInvariant()}");
        Console.WriteLine($"pane: {target.Pane}");
        Console.WriteLine($"pane_exists: {paneExists.ToString().ToLowerInvariant()}");
        if (!paneExists)
        {
            return 1;
        }

        var process = runner.CurrentProcess(target);
        Console.WriteLine($"current_command: {process?.Command ?? "unknown"}");
        Console.WriteLine($"pane_pid: {process?.Pid ?? "unknown"}");

        var result = runner.Capture(target, ParseInt(options.GetValueOrDefault("lines") ?? "20", "--lines"));
        Console.WriteLine($"capture_success: {(result.ReturnCode == 0).ToString().ToLowerInvariant()}");
        if (result.ReturnCode == 0 && result.Stdout.Length > 0)
        {
            Console.WriteLine("capture:");
            Console.Write(result.Stdout);
        }
        else if (result.ReturnCode != 0)
        {
            Console.Error.Write(result.Stderr);
        }

        return result.ReturnCode;
    }

    private static int StopAgent(
        Dictionary<string, string?> options,
        TmuxRunner runner,
        AgentCommandBuilder builder)
    {
        var target = ParseTarget(options);
        var agent = RequireChoice(options, "agent", AgentChoices);
        if (!runner.DryRun && (!runner.HasSession(target) || !runner.HasPane(target)))
        {
            throw new CliException($"Target pane does not exist: {target.Value}");
        }

        runner.SendKeys(target, builder.ExitInput(agent), "Enter");
        if (options.ContainsKey("kill-session"))
        {
            runner.KillSession(target);
        }

        return 0;
    }

    private static int SleepOnly(Dictionary<string, string?> options, TmuxRunner runner)
    {
        runner.Sleep(ParseSleepSeconds(Require(options, "__arg0")));
        return 0;
    }

    private static Dictionary<string, string?> ParseOptions(string[] args)
    {
        var options = new Dictionary<string, string?>(StringComparer.Ordinal);
        var positional = 0;
        for (var i = 0; i < args.Length; i++)
        {
            var arg = args[i];
            if (!arg.StartsWith("--", StringComparison.Ordinal))
            {
                options[$"__arg{positional++}"] = arg;
                continue;
            }

            var key = arg[2..];
            if (key is "dry-run" or "capture-after-sleep" or "kill-session")
            {
                options[key] = null;
                continue;
            }

            if (i + 1 >= args.Length)
            {
                throw new CliException($"missing value for {arg}");
            }

            options[key] = args[++i];
        }

        return options;
    }

    private static TmuxTarget ParseTarget(Dictionary<string, string?> options)
    {
        var pane = Require(options, "pane");
        if (!PaneRegex().IsMatch(pane))
        {
            throw new CliException("--pane must be in window.pane format, for example 0.0");
        }

        return new TmuxTarget(Require(options, "session"), pane);
    }

    private static (int Cols, int Rows) ParseSize(string size)
    {
        var match = SizeRegex().Match(size);
        if (!match.Success)
        {
            throw new CliException("--size must be in COLSxROWS format, for example 220x60");
        }

        var cols = int.Parse(match.Groups[1].Value);
        var rows = int.Parse(match.Groups[2].Value);
        if (cols <= 0 || rows <= 0)
        {
            throw new CliException("--size values must be positive");
        }

        return (cols, rows);
    }

    private static string ResolveCwd(string cwd)
    {
        var path = Path.GetFullPath(Environment.ExpandEnvironmentVariables(cwd));
        if (!Directory.Exists(path))
        {
            throw new CliException($"--cwd must be an existing directory: {path}");
        }

        return path;
    }

    private static double ParseSleepSeconds(string seconds)
    {
        if (!double.TryParse(seconds, out var value))
        {
            throw new CliException("sleep seconds must be a number");
        }

        if (value < 0)
        {
            throw new CliException("sleep seconds must be zero or positive");
        }

        return value;
    }

    private static int ParseInt(string value, string name)
    {
        if (!int.TryParse(value, out var parsed))
        {
            throw new CliException($"{name} must be an integer");
        }

        return parsed;
    }

    private static string FormatSeconds(double seconds)
    {
        return Math.Abs(seconds - Math.Truncate(seconds)) < double.Epsilon
            ? ((int)seconds).ToString()
            : seconds.ToString("G");
    }

    private static string Require(Dictionary<string, string?> options, string key)
    {
        if (!options.TryGetValue(key, out var value) || value is null)
        {
            throw new CliException($"--{key} is required");
        }

        return value;
    }

    private static string RequireChoice(
        Dictionary<string, string?> options,
        string key,
        HashSet<string> choices)
    {
        var value = Require(options, key);
        if (!choices.Contains(value))
        {
            throw new CliException($"--{key} has unsupported value: {value}");
        }

        return value;
    }

    private static string ShellQuote(string value)
    {
        if (value.Length == 0)
        {
            return "''";
        }

        return value.Any(ch => char.IsWhiteSpace(ch) || "'\"\\$`!&|;<>()*?[]{}".Contains(ch))
            ? $"'{value.Replace("'", "'\"'\"'")}'"
            : value;
    }

    private static string JoinCommand(IEnumerable<string> args)
    {
        return string.Join(" ", args.Select(ShellQuote));
    }

    [GeneratedRegex(@"^\d+\.\d+$")]
    private static partial Regex PaneRegex();

    [GeneratedRegex(@"^(\d+)x(\d+)$")]
    private static partial Regex SizeRegex();

    private sealed record AgentCommandSpec(string Agent, string Mode, string? Model, string Cwd);

    private sealed record TmuxTarget(string Session, string Pane)
    {
        public string Value => $"{Session}:{Pane}";
    }

    private sealed record CommandResult(int ReturnCode, string Stdout, string Stderr);

    private sealed record PaneProcess(string Command, string Pid)
    {
        public bool IsShell => ShellCommands.Contains(Path.GetFileName(Command));
    }

    private sealed class AgentCommandBuilder
    {
        public string Build(AgentCommandSpec spec)
        {
            if (spec.Agent == "codex")
            {
                RequireMode(spec, "start");
                return $"codex --no-alt-screen -C {ShellQuote(spec.Cwd)} -s workspace-write -a on-request";
            }

            if (spec.Agent == "claude")
            {
                RequireMode(spec, "start");
                return "TERM=dumb claude";
            }

            if (spec.Agent == "copilot")
            {
                var model = RequireModel(spec);
                return spec.Mode switch
                {
                    "start" => $"copilot --model {model} --no-ask-user",
                    "continue" => $"copilot --continue --model {model} --no-ask-user",
                    _ => throw new CliException($"Unsupported agent/mode combination: {spec.Agent}/{spec.Mode}"),
                };
            }

            throw new CliException($"Unsupported agent/mode combination: {spec.Agent}/{spec.Mode}");
        }

        public string ExitInput(string agent)
        {
            if (AgentChoices.Contains(agent))
            {
                return "/exit";
            }

            throw new CliException($"Unsupported agent: {agent}");
        }

        public string DefaultModeForEnsure(string agent)
        {
            return agent switch
            {
                "copilot" => "continue",
                "codex" or "claude" => "start",
                _ => throw new CliException($"Unsupported agent: {agent}"),
            };
        }

        private static void RequireMode(AgentCommandSpec spec, string expected)
        {
            if (spec.Mode != expected)
            {
                throw new CliException($"{spec.Agent} supports only {expected} mode");
            }
        }

        private static string RequireModel(AgentCommandSpec spec)
        {
            if (string.IsNullOrWhiteSpace(spec.Model))
            {
                throw new CliException("copilot requires --model");
            }

            return spec.Model;
        }
    }

    private sealed class TmuxRunner(bool dryRun)
    {
        public bool DryRun { get; } = dryRun;

        public CommandResult Run(IReadOnlyList<string> args)
        {
            if (DryRun)
            {
                Console.WriteLine(JoinCommand(args));
                return new CommandResult(0, string.Empty, string.Empty);
            }

            using var process = new Process();
            process.StartInfo.FileName = args[0];
            foreach (var arg in args.Skip(1))
            {
                process.StartInfo.ArgumentList.Add(arg);
            }

            process.StartInfo.RedirectStandardOutput = true;
            process.StartInfo.RedirectStandardError = true;
            process.StartInfo.UseShellExecute = false;
            process.Start();
            var stdout = process.StandardOutput.ReadToEnd();
            var stderr = process.StandardError.ReadToEnd();
            process.WaitForExit();
            return new CommandResult(process.ExitCode, stdout, stderr);
        }

        public bool HasSession(TmuxTarget target)
        {
            return Run(["tmux", "has-session", "-t", target.Session]).ReturnCode == 0;
        }

        public bool HasPane(TmuxTarget target)
        {
            var result = Run(
            [
                "tmux",
                "list-panes",
                "-t",
                $"{target.Session}:0",
                "-F",
                "#{window_index}.#{pane_index}",
            ]);
            return result.ReturnCode == 0 &&
                result.Stdout.Split('\n', StringSplitOptions.RemoveEmptyEntries).Contains(target.Pane);
        }

        public CommandResult Capture(TmuxTarget target, int lines)
        {
            return Run(["tmux", "capture-pane", "-t", target.Value, "-p", "-S", $"-{lines}"]);
        }

        public void Sleep(double seconds)
        {
            if (DryRun)
            {
                Console.WriteLine($"sleep {FormatSeconds(seconds)}");
                return;
            }

            Thread.Sleep(TimeSpan.FromSeconds(seconds));
        }

        public PaneProcess? CurrentProcess(TmuxTarget target)
        {
            var result = Run(
            [
                "tmux",
                "display-message",
                "-p",
                "-t",
                target.Value,
                "#{pane_current_command}\t#{pane_pid}",
            ]);
            if (result.ReturnCode != 0)
            {
                return null;
            }

            var parts = result.Stdout.Trim().Split('\t');
            return parts.Length == 2 && parts[0].Length > 0 ? new PaneProcess(parts[0], parts[1]) : null;
        }

        public void NewSession(TmuxTarget target, string cwd, int cols, int rows)
        {
            MustRun(["tmux", "new-session", "-d", "-s", target.Session, "-x", cols.ToString(), "-y", rows.ToString(), "-c", cwd]);
        }

        public void SplitWindow(TmuxTarget target, string cwd, string split, string? splitFrom)
        {
            var tmuxTarget = splitFrom is null ? target.Session : $"{target.Session}:{splitFrom}";
            var flag = split == "vertical" ? "-v" : "-h";
            MustRun(["tmux", "split-window", flag, "-t", tmuxTarget, "-c", cwd]);
        }

        public void SendKeys(TmuxTarget target, params string[] keys)
        {
            MustRun(["tmux", "send-keys", "-t", target.Value, .. keys]);
        }

        public void LoadAndPaste(TmuxTarget target, string promptFile)
        {
            MustRun(["tmux", "load-buffer", promptFile]);
            MustRun(["tmux", "paste-buffer", "-t", target.Value]);
        }

        public void KillSession(TmuxTarget target)
        {
            MustRun(["tmux", "kill-session", "-t", target.Session]);
        }

        private void MustRun(IReadOnlyList<string> args)
        {
            var result = Run(args);
            if (result.ReturnCode != 0)
            {
                throw new CliException(result.Stderr.Trim().Length > 0 ? result.Stderr.Trim() : "tmux command failed");
            }
        }
    }

    private sealed class CliException(string message) : Exception(message);
}
