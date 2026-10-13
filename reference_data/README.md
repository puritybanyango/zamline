# Gemini reference files

Place the approved Markdown reference files used by the cost-assessment feature in
this directory on the application server. The Gemini integration checks whether a
previously uploaded file reference is still available and re-uploads the original
Markdown file when needed.

The runtime Gemini file names, URIs, MIME types and upload timestamps are stored in
`data/gemini_file_state.json`. That runtime state file is not committed.
