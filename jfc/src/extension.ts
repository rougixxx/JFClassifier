// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import fetch from 'node-fetch';

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {
    console.log('Java function classifier extension is now active!');

    let disposable = vscode.commands.registerCommand('jfc.classifyFunction', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor!');
            return;
        }

        const code = editor.document.getText(editor.selection) || editor.document.getText();

        await vscode.window.withProgress(
            {
                location: vscode.ProgressLocation.Notification,
                title: "Classifying the selected Function",
                cancellable: false
            },
            async (progress) => {
                try {
                    progress.report({ increment: 20, message: "Sending code..." });

                    const response = await fetch('http://127.0.0.1:8000/api/predict', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ code })
                    });

                    progress.report({ increment: 70, message: "Your function is being processed..." });

                    const data = await response.json();

                    // Highlight result in editor
                    const decorationType = vscode.window.createTextEditorDecorationType({
                        backgroundColor: data.prediction === "VULNERABLE" ? "rgba(255,0,0,0.3)" : "rgba(53, 231, 17, 0.5)"
                    });
                    editor.setDecorations(decorationType, [editor.selection]);

                    progress.report({ increment: 100, message: "Done!" });
                    vscode.window.showInformationMessage(`Prediction Result: ${data.prediction}`);
                } catch (err) {
                    vscode.window.showErrorMessage(`Error calling API: ${err}`);
                }
            }
        );
    });

    context.subscriptions.push(disposable);
}

export function deactivate() {}
