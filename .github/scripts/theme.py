"""Shared design tokens for every generated SVG in this profile."""

BG = "#0D1117"
PANEL = "#161B22"
LINE = "#30363D"
MUTED = "#8B949E"
WHITE = "#F8FAFC"
PURPLE = "#A855F7"
CYAN = "#22D3EE"
AMBER = "#F59E0B"

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"

# Every animated SVG switches to its finished state for reduced-motion users.
REDUCED_MOTION = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
