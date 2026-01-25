# Missing CFB Coordinates

The following five coordinates are present in our mined key set but absent from the Mystery Lab seed extraction. They are critical for the bridge architecture.

| # | Coordinate | Seed (first 55 chars, lower) | Documented Identity | Real Identity (Qubic) | Remarks |
|---|------------|------------------------------|--------------------|-----------------------|---------|
| 1 | (45, 92) | `aaaaaaaaaewamanayeyaaaaaywrlaebhiepesefaeejreqtremjchof` | `AAAAAAAAAEWAMANAYEYAAAAAYWRLAEBHIEPESEFAEEJREQTREMJCHOFFIFHJ` | `HSISJEJOTMWHNBDGGBTEIYKHQLXBAGCUVTWNKMEHGDWCECFHVAGSTGLBOPKE` | First signature (α ≈ 1/137) – missing because Lab only extracted seeds from documented identities. |
| 2 | (84, 37) | `aaaaaaaaewamanayeyaaaaaywrlaebhiepesefaeejreqtremjchoffv` | `AAAAAAAAEWAMANAYEYAAAAAYWRLAEBHIEPESEFAEEJREQTREMJCHOFFVMFUEE` | `LUEKURCZPASWTBBPUKJABTEXJWIAMEPHFQOANMAFUAKSDJCSIJHZETOGQHPH` | Collision‑Weight signature – not in Lab data. |
| 3 | (96, 7) | `aaaaaaaaawamanayeyaaaaaywrlaebhiepesefaeejreqtremjchofv` | `AAAAAAAAAWAMANAYEYAAAAAYWRLAEBHIEPESEFAEEJREQTREMJCHOFFVMFUEE` | Same as above – missing for same reason. |
| 4 | (87, 43) | `aaaaaaaaaewamanayeyaaaaaywrlaebhiepesefaeejreqtremjchofw` | `AAAAAAAAAEWAMANAYEYAAAAAYWRLAEBHIEPESEFAEEJREQTREMJCHOFFVMFUEE` | Same as above – missing. |
| 5 | (82, 39) | `aaaaaaaaaewamanayeyaaaaaywrlaebhiepesefaeejreqtremjchofx` | `AAAAAAAAAEWAMANAYEYAAAAAYWRLAEBHIEPESEFAEEJREQTREMJCHOFFVMFUEE` | Exit node – critical coordinate, deliberately omitted from Lab extraction. |

These coordinates are highlighted in the main proof document under the **Missing CFB Coordinates** section.
