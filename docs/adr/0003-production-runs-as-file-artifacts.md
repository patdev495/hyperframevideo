# Production runs as file artifacts

Each video production attempt will be stored as a directory under `.runs/<run-id>/` containing source evidence, selected story, script, storyboard, design notes, voiceover, transcript, HyperFrames compositions, assets, and rendered output. File-based production runs make the CLI MVP resumable and inspectable, and they give a later web UI a stable artifact model to read from instead of forcing an early database design.
