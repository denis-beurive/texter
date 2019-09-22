# Synopsis

This repository contains a Python script that can be used to
split a binary file into a series of smaller text files (called
"parts").

The contents of the generated text files (the "parts") are designed
to be easily manipulated.

Examples of parts:

file `part-1-9.part`:

This is the first part within a series of 9 parts.
`27abd963213207d2c0882362d67fddd8` is the MD5 sum of the text
between the boundaries "`------...`".

    000001
    000009
    27abd963213207d2c0882362d67fddd8
    ----------------------------------------------------------
    TG9yZW0gaXBzdW0gZG9sb3Igc2l0IGFtZXQsIGNvbnNlY3RldHVyIGFkaXB
    pc2NpbmcgZWxpdC4gRHVpcyBzaXQgYW1ldCBpcHN1bSBldCBvZGlvIGltcG
    VyZGlldCBjb25zZWN0ZXR1ci4gTWFlY2VuYXMgZXVpc21vZCBlcmF0IG5pc
    2wsIHZ1bHB1dGF0ZSBmaW5pYnVzIG5pYmggYmxhbmRpdCBzaXQgYW1ldC4g
    Vml2YW11cyBibGFuZGl0IGNvbmd1ZSBkb2xvciBhYyB2ZWhpY3VsYS4gRG9
    uZWMgc2FnaXR0aXMgZWdldCBkdWkgYWMgcG9ydHRpdG9yLiBRdWlzcXVlIH
    RlbXB1cyBudW5jIGlkIHNlbXBlciBkaWduaXNzaW0uIEN1cmFiaXR1ciBzZ
    W1wZXIgbGFjdXMgcG9ydHRpdG9yLCBjb21tb2RvIGRpYW0gbm9uLCB0ZW1w
    dXMgdHVycGlzLiBNYXVyaXMgZ3JhdmlkYSBzYXBpZW4gdml0YWUgbnVuYyB
    hbGlxdWV0IHRpbmNpZHVudC4gTW9yYmkgdGVtcHVzIHF1YW0gZXJhdCwgbm
    VjIGNvbmd1ZSBhdWd1ZSBlZmZpY2l0dXIgaWQuIE1hZWNlbmFzIHZ1bHB1d
    GF0ZSwgYW50ZSBzaXQgYW1ldCBpbXBlcmRpZXQgdWx0cmljaWVzLCBtYXVy
    aXMgcmlzdXMgY29uZGltZW50dW0gaXBzdW0sIHF1aXMgbGFvcmVldCBlbGl
    0IGZlbGlzIHV0IG5lcXVlLiBBbGlxdWFtIGluIGxlbyBhbGlxdWV0LCBwb3
    J0YSBsb3JlbSBpZCwgc
    ----------------------------------------------------------

file `part-2-9.part`:

This is the second part within a series of 9 parts.
`5335a472ac390f33bbc3a5a592ca68c3` is the MD5 sum of the text
between the boundaries "`------...`".

    000002
    000009
    5335a472ac390f33bbc3a5a592ca68c3
    ----------------------------------------------------------
    29sbGljaXR1ZGluIG5pc2kuIEFlbmVhbiBvcmNpIGVyYXQsIHNlbXBlciBh
    dCBvcm5hcmUgc2l0IGFtZXQsIHZlaGljdWxhIGluIG51bGxhLgoKRXRpYW0
    gYXJjdSBwdXJ1cywgc3VzY2lwaXQgbmVjIGV1aXNtb2Qgbm9uLCB0aW5jaW
    R1bnQgdml0YWUgbWV0dXMuIEZ1c2NlIG5vbiBvZGlvIGZhdWNpYnVzLCBka
    WN0dW0gYXJjdSBldCwgY29uZ3VlIG51bmMuIEN1cmFiaXR1ciB2ZWhpY3Vs
    YSBudW5jIGF0IG1pIGZldWdpYXQgYWNjdW1zYW4uIFNlZCBhbGlxdWFtIGZ
    lbGlzIGluIGZlbGlzIGV1aXNtb2QgZmVybWVudHVtIHNpdCBhbWV0IGV0IG
    RvbG9yLiBEdWlzIHV0IGZlbGlzIGxvcmVtLiBQcm9pbiBzYWdpdHRpcyBqd
    XN0byBhdCBvZGlvIGRhcGlidXMsIGVnZXQgcG9ydHRpdG9yIHR1cnBpcyBp
    bXBlcmRpZXQuIEFlbmVhbiBhdCBjdXJzdXMgb2RpbywgaWQgY3Vyc3VzIHR
    lbGx1cy4gUGVsbGVudGVzcXVlIHNpdCBhbWV0IGRvbG9yIGFyY3UuIFV0IG
    FsaXF1ZXQgZmVsaXMgbW9sZXN0aWUgbGFjdXMgYWxpcXVldCwgcXVpcyB0Z
    W1wdXMgbWkgZmVybWVudHVtLiBTZWQgZG9sb3IgbWV0dXMsIGV1aXNtb2Qg
    aWQgdHVycGlzIGV1LCBpYWN1bGlzIGx1Y3R1cyB1cm5hLiBRdWlzcXVlIG5
    1bmMgbWF1cmlzLCBlbG
    ----------------------------------------------------------

# Usage

## Split a binary file into parts

    python texter.py b2a \
           [--dir=<directory where to store the parts>] \
           [--stem=<parts stem>] \
           [--max-char=<number of characters per part>] \
           --input=<path to the binary file to split>

## Build a file from parts

    python texter.py a2b \
           [--dir=<directory where to store the parts>] \
           [--stem=<parts stem>] \
           --output=<path to the binary file to build>
