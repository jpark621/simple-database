# Simple Database
Simple database

Includes
  - hash index
  - compaction of segments

## Time
This took around 4h.

## Claude Code Review
Critical bugs:
  - db_get did not get segment number (typo) \[FIXED\]
  - type switching with keys caused failures when getting key from old segments \[FIXED\]
  - when writing to new segment, you should check SEGMENT_SIZE >= offset, not == \[FIXED\]

Missing features:
  - tombstone for deletion
  - crash recovery (index recovery)
  - in-memory index is limiting(?)
  - no WAL
  - no checksum (cannot check file-corruption)