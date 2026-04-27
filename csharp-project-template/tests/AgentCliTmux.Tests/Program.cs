using System.Diagnostics;

namespace AgentCliTmux.Tests;

internal static class Program
{
    private static readonly string RepoRoot = FindRepoRoot();
    private static readonly string ToolProject = Path.Combine(RepoRoot, "tools", "AgentCliTmux");

    public static int Main()
    {
        var tests = new (string Name, Action Body)[]
        {
            ("start dry-run prints new session and send keys", StartDryRunPrintsTmuxNewSessionAndSendKeys),
            ("start dry-run keeps cwd with spaces", StartDryRunKeepsCwdWithSpaces),
            ("start dry-run builds claude command", StartDryRunBuildsClaudeCommand),
            ("ensure dry-run uses default ensure mode", EnsureDryRunUsesDefaultEnsureMode),
            ("copilot requires model", CopilotRequiresModel),
            ("send-prompt dry-run prints buffer and enter", SendPromptDryRunPrintsBufferAndEnter),
            ("send-prompt dry-run can sleep then capture", SendPromptDryRunCanSleepThenCapture),
            ("send-prompt dry-run can delay submit then sleep then capture", SendPromptDryRunCanDelaySubmitThenSleepThenCapture),
            ("send-prompt dry-run allows missing file", SendPromptDryRunAllowsMissingFile),
            ("stop dry-run sends exit to pane", StopDryRunSendsExitToPane),
            ("sleep dry-run prints sleep duration", SleepDryRunPrintsSleepDuration),
            ("sleep rejects negative duration", SleepRejectsNegativeDuration),
            ("invalid pane returns error", InvalidPaneReturnsError),
        };

        var failed = 0;
        foreach (var (name, body) in tests)
        {
            try
            {
                body();
                Console.WriteLine($"PASS {name}");
            }
            catch (Exception e)
            {
                failed++;
                Console.Error.WriteLine($"FAIL {name}: {e.Message}");
            }
        }

        Console.WriteLine($"{tests.Length - failed}/{tests.Length} tests passed");
        return failed == 0 ? 0 : 1;
    }

    private static void StartDryRunPrintsTmuxNewSessionAndSendKeys()
    {
        var result = RunTool(
            "start",
            "--dry-run",
            "--session",
            "template-test",
            "--pane",
            "0.0",
            "--cwd",
            RepoRoot,
            "--agent",
            "codex");

        AssertEqual(0, result.ExitCode);
        AssertContains("tmux new-session -d -s template-test", result.Stdout);
        AssertContains("tmux send-keys -t template-test:0.0", result.Stdout);
        AssertContains("codex --no-alt-screen", result.Stdout);
    }

    private static void StartDryRunKeepsCwdWithSpaces()
    {
        var cwd = Path.Combine(Path.GetTempPath(), $"agent-cli-tmux test {Guid.NewGuid():N}");
        Directory.CreateDirectory(cwd);
        try
        {
            var result = RunTool(
                "start",
                "--dry-run",
                "--session",
                "template-test",
                "--pane",
                "0.0",
                "--cwd",
                cwd,
                "--agent",
                "codex");

            AssertEqual(0, result.ExitCode);
            AssertContains(cwd, result.Stdout);
            AssertContains("codex --no-alt-screen -C", result.Stdout);
        }
        finally
        {
            Directory.Delete(cwd, recursive: true);
        }
    }

    private static void StartDryRunBuildsClaudeCommand()
    {
        var result = RunTool(
            "start",
            "--dry-run",
            "--session",
            "template-test",
            "--pane",
            "0.0",
            "--cwd",
            RepoRoot,
            "--agent",
            "claude");

        AssertEqual(0, result.ExitCode);
        AssertContains("TERM=dumb claude", result.Stdout);
    }

    private static void EnsureDryRunUsesDefaultEnsureMode()
    {
        var result = RunTool(
            "ensure",
            "--dry-run",
            "--session",
            "template-test",
            "--pane",
            "0.0",
            "--cwd",
            RepoRoot,
            "--agent",
            "copilot",
            "--model",
            "claude-sonnet-4.6");

        AssertEqual(0, result.ExitCode);
        AssertContains("copilot --continue --model claude-sonnet-4.6 --no-ask-user", result.Stdout);
    }

    private static void CopilotRequiresModel()
    {
        var result = RunTool(
            "start",
            "--dry-run",
            "--session",
            "template-test",
            "--pane",
            "0.0",
            "--cwd",
            RepoRoot,
            "--agent",
            "copilot");

        AssertEqual(2, result.ExitCode);
        AssertContains("copilot requires --model", result.Stderr);
    }

    private static void SendPromptDryRunPrintsBufferAndEnter()
    {
        var promptFile = CreatePromptFile();
        try
        {
            var result = RunTool(
                "send-prompt",
                "--dry-run",
                "--session",
                "template-test",
                "--pane",
                "0.1",
                "--file",
                promptFile);

            AssertEqual(0, result.ExitCode);
            AssertContains($"tmux load-buffer {promptFile}", result.Stdout);
            AssertContains("tmux paste-buffer -t template-test:0.1", result.Stdout);
            AssertContains("tmux send-keys -t template-test:0.1 Enter", result.Stdout);
        }
        finally
        {
            File.Delete(promptFile);
        }
    }

    private static void SendPromptDryRunCanSleepThenCapture()
    {
        var promptFile = CreatePromptFile();
        try
        {
            var result = RunTool(
                "send-prompt",
                "--dry-run",
                "--session",
                "template-test",
                "--pane",
                "0.1",
                "--file",
                promptFile,
                "--sleep-after",
                "5",
                "--capture-after-sleep",
                "--lines",
                "320");

            AssertEqual(0, result.ExitCode);
            AssertContains("tmux send-keys -t template-test:0.1 Enter", result.Stdout);
            AssertContains("sleep 5", result.Stdout);
            AssertContains("tmux capture-pane -t template-test:0.1 -p -S -320", result.Stdout);
        }
        finally
        {
            File.Delete(promptFile);
        }
    }

    private static void SendPromptDryRunCanDelaySubmitThenSleepThenCapture()
    {
        var promptFile = CreatePromptFile();
        try
        {
            var result = RunTool(
                "send-prompt",
                "--dry-run",
                "--session",
                "template-test",
                "--pane",
                "0.1",
                "--file",
                promptFile,
                "--submit-delay",
                "5",
                "--sleep-after",
                "10",
                "--capture-after-sleep",
                "--lines",
                "320");

            AssertEqual(0, result.ExitCode);
            var expected = string.Join(
                Environment.NewLine,
                [
                    $"tmux load-buffer {Path.GetFullPath(promptFile)}",
                    "tmux paste-buffer -t template-test:0.1",
                    "sleep 5",
                    "tmux send-keys -t template-test:0.1 Enter",
                    "sleep 10",
                    "tmux capture-pane -t template-test:0.1 -p -S -320",
                    string.Empty,
                ]);
            AssertEqual(expected, result.Stdout);
        }
        finally
        {
            File.Delete(promptFile);
        }
    }

    private static void SendPromptDryRunAllowsMissingFile()
    {
        var missingPromptFile = Path.Combine(RepoRoot, "tmp", "template_missing_prompt_for_dry_run.md");

        var result = RunTool(
            "send-prompt",
            "--dry-run",
            "--session",
            "template-test",
            "--pane",
            "0.1",
            "--file",
            missingPromptFile);

        AssertEqual(0, result.ExitCode);
        AssertContains($"tmux load-buffer {Path.GetFullPath(missingPromptFile)}", result.Stdout);
    }

    private static void StopDryRunSendsExitToPane()
    {
        var result = RunTool(
            "stop",
            "--dry-run",
            "--session",
            "template-test",
            "--pane",
            "0.0",
            "--agent",
            "claude");

        AssertEqual(0, result.ExitCode);
        AssertContains("tmux send-keys -t template-test:0.0 /exit Enter", result.Stdout);
    }

    private static void SleepDryRunPrintsSleepDuration()
    {
        var result = RunTool("sleep", "--dry-run", "30");

        AssertEqual(0, result.ExitCode);
        AssertEqual($"sleep 30{Environment.NewLine}", result.Stdout);
    }

    private static void SleepRejectsNegativeDuration()
    {
        var result = RunTool("sleep", "--dry-run", "-1");

        AssertEqual(2, result.ExitCode);
        AssertContains("sleep seconds must be zero or positive", result.Stderr);
    }

    private static void InvalidPaneReturnsError()
    {
        var result = RunTool(
            "start",
            "--dry-run",
            "--session",
            "template-test",
            "--pane",
            "0",
            "--cwd",
            RepoRoot,
            "--agent",
            "claude");

        AssertEqual(2, result.ExitCode);
        AssertContains("--pane must be in window.pane format", result.Stderr);
    }

    private static CommandResult RunTool(params string[] args)
    {
        using var process = new Process();
        process.StartInfo.FileName = "dotnet";
        process.StartInfo.ArgumentList.Add("run");
        process.StartInfo.ArgumentList.Add("--project");
        process.StartInfo.ArgumentList.Add(ToolProject);
        process.StartInfo.ArgumentList.Add("--");
        foreach (var arg in args)
        {
            process.StartInfo.ArgumentList.Add(arg);
        }

        process.StartInfo.RedirectStandardOutput = true;
        process.StartInfo.RedirectStandardError = true;
        process.StartInfo.UseShellExecute = false;
        process.StartInfo.WorkingDirectory = RepoRoot;
        process.Start();
        var stdout = process.StandardOutput.ReadToEnd();
        var stderr = process.StandardError.ReadToEnd();
        process.WaitForExit();
        return new CommandResult(process.ExitCode, stdout, stderr);
    }

    private static string CreatePromptFile()
    {
        var path = Path.Combine(Path.GetTempPath(), $"agent-cli-tmux-prompt-{Guid.NewGuid():N}.md");
        File.WriteAllText(path, "review this\n");
        return path;
    }

    private static string FindRepoRoot()
    {
        var directory = new DirectoryInfo(Directory.GetCurrentDirectory());
        while (directory is not null)
        {
            var candidate = Path.Combine(directory.FullName, "tools", "AgentCliTmux", "AgentCliTmux.csproj");
            if (File.Exists(candidate))
            {
                return directory.FullName;
            }

            var nestedCandidate = Path.Combine(
                directory.FullName,
                "csharp-project-template",
                "tools",
                "AgentCliTmux",
                "AgentCliTmux.csproj");
            if (File.Exists(nestedCandidate))
            {
                return Path.Combine(directory.FullName, "csharp-project-template");
            }

            directory = directory.Parent;
        }

        throw new InvalidOperationException("Could not find csharp-project-template root.");
    }

    private static void AssertContains(string expectedSubstring, string actual)
    {
        if (!actual.Contains(expectedSubstring, StringComparison.Ordinal))
        {
            throw new InvalidOperationException(
                $"Expected output to contain '{expectedSubstring}', actual: '{actual}'.");
        }
    }

    private static void AssertEqual<T>(T expected, T actual)
    {
        if (!EqualityComparer<T>.Default.Equals(expected, actual))
        {
            throw new InvalidOperationException($"Expected '{expected}', actual '{actual}'.");
        }
    }

    private sealed record CommandResult(int ExitCode, string Stdout, string Stderr);
}
