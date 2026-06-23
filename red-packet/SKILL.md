---
name: red-packet
description: redpacket,send,pending,claim,history,.pie,XLayer USDT0
---

# Red Packet

## Overview

This Skill covers P2P XLayer USDT0 redpackets: sending redpackets to `.pie`
handles or raw EVM addresses, checking pending redpackets, claiming received
redpackets, and reviewing sent history.

Pick the relevant command group from the table, then read that reference before
running commands or explaining the workflow.

## Out of Scope

- `purr .pie transfer` for direct `.pie` transfers.
- `purr wallet transfer` for raw wallet transfers.

## Command Groups

| Group | What It Does | Reference |
|---|---|
| Send / Sent History | Sends redpackets to `.pie` handles or raw EVM addresses, handles trusted chat-channel metadata, and reviews sent redpacket history. | [send.md](references/send.md) |
| Pending / Claim | Checks claimable redpackets, claims all pending redpackets, claims by sender, or claims selected envelope ids. | [claim.md](references/claim.md) |
