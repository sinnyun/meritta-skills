---
name: figcraft-operator
description: Create and edit native FigCraft design files with the installed FigCraft app or CLI, including editable UI references, prototypes, components, and exports. Use when the requested deliverable belongs in FigCraft; do not treat this as permission to change a referenced application's source code.
disable-model-invocation: true
---

# FigCraft Operator

Use FigCraft's document model to make native, editable `.figcraft` files. Keep requested design work independent from the source code of any application being represented unless the user separately asks for an implementation.

## Choose the operating mode

- For a new standalone file, use the installed `figcraft-cli` MCP server (`figcraft-cli mcp`) or command runner (`figcraft-cli run`). These use the same document engine as the desktop app and produce native files.
- To edit a document the user already has open and see changes live, use the CLI MCP server attached to the desktop app (`figcraft-cli mcp --attach PORT`) when the app was started with its loopback control channel.
- Use FigCraft's `inspect_document`, `get_node`, `inspect_ui`, `screenshot`, or CLI `info`/`render` to check the saved document. Keep layers, labels, and controls separate so the user can refine them.

## Design workflow

1. Read the referenced product's available screens, component structure, and visual evidence. Separate visible facts from details that must be inferred.
   - For a running Electron/Chromium product, prefer read-only CDP DOM inspection when available. Measure `getBoundingClientRect()` and computed styles for visible regions and controls; record text, `placeholder`, `value`, selected options, borders, colors, radius, font, and stacking order. Keep CSS pixel values and record `devicePixelRatio` so physical pixels can be derived (`device px = CSS px × DPR`).
   - Avoid saving private/user data from file lists, notes, or resource names. Capture representative labels and UI structure, and redact content fields unless the user explicitly needs them.
   - DOM inspection measures HTML controls and the bounds of `<canvas>` elements. It does not expose individual objects painted inside Canvas/WebGL; inspect the app's documented scene/model data for those, and label any inferred details.
2. Turn each requested screen or state into a named FigCraft page or frame. Recreate panel geometry, toolbars, navigation, controls, labels, dropdowns, and representative content as editable layers.
3. When the reference has repeated visual patterns, build a component library first and assemble screens from component instances. Use component properties for labels and values, and variants for recurring visual states or sizes. Avoid styling each repeated button or row independently.
4. Prefer explicit, named frames and groups for the major interface regions. Use text and native shapes for controls so the file remains easy to optimize by hand.
5. Save to the exact requested `.figcraft` path. Render or inspect the saved file and correct obvious layout, text, or clipping problems before delivery.
6. When a screen-state can be changed through the product's supported MCP/API, use that interface to enter the state before taking read-only DOM measurements. Do not use DOM click/dispatch or mouse/keyboard automation to change the product state.

## Local CLI and MCP

This machine has FigCraft 0.12.1 installed under `C:\Program Files\FigCraft`; resolve the executable there or from `PATH` rather than assuming a machine-wide command alias exists. The CLI command list and MCP tool schemas are authoritative for the installed version.

The MCP server uses newline-delimited JSON-RPC over stdio. Useful tools include `run_command`, `create_node`, `set_properties`, `inspect_document`, `get_node`, `screenshot`, `open_file`, and `save_file`. For repeatable headless document generation, `figcraft-cli run plan.json --out output.figcraft` executes the same command registry without opening dialogs. Use `figcraft-cli info` and `figcraft-cli render` to inspect or export a saved file.

When using the headless MCP server, pass existing `--automation-read-root` and `--automation-write-root` folders that cover only the source material and output location needed for the task. Do not pass these flags to an attached MCP server; the running app enforces its own roots.

Reference documentation:

- [FigCraft repository](https://github.com/storytold/figcraft)
- [MCP tools and command workflow](https://github.com/storytold/figcraft/blob/main/docs/mcp.md)
- [CLI commands](https://github.com/storytold/figcraft/blob/main/docs/cli.md)
- [Desktop control protocol](https://github.com/storytold/figcraft/blob/main/docs/control-protocol.md)
