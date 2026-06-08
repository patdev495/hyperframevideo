# Use HyperFrames as a dependency, not a fork

The project will not fork or copy the HyperFrames upstream repository into this repo for the MVP. This repo owns the News-to-Video Pipeline and will use HyperFrames packages, templates, CLI behavior, and documentation as the rendering dependency, keeping upstream exploration separate from product code unless a later integration requires explicit vendoring.
