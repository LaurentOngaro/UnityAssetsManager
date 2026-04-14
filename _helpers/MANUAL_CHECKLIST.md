# UnityAssetsManager - Manual Checklist (Include/Exclude + Profiles)

## Run scripted checks

```powershell
pwsh -NoProfile -File _Helpers/04_Assets/UnityAssetsManager/_helpers/runManualChecklist.ps1
```

Optional parameters:

```powershell
pwsh -NoProfile -File _Helpers/04_Assets/UnityAssetsManager/_helpers/runManualChecklist.ps1 -BaseUrl http://localhost:5003 -OutputDir exports/manual_checklist
```

NOTE: 5003 is the default port for the web interface, but the it can be changed in `config/config.json`

## UI checklist

- [ ] Add an `include` filter on `DisplayCategory=Tools`
- [ ] Add an `exclude` filter on `DisplayPublisher=PublisherB`
- [ ] Click `Apply` and verify the filtered table no longer contains `PublisherB`
- [ ] Save a profile from the UI with both filters
- [ ] Reload this profile and confirm include/exclude modes are preserved
- [ ] Open export modal and verify row counters are consistent
- [ ] Export in available formats and verify generated file extensions

## Expected API checks from script

- `/api/templates` reachable
- `POST /api/profiles` saves a profile with include/exclude stack
- `GET /api/profiles/{name}` restores include/exclude modes
- `POST /api/batch-export` validates extension mapping for available formats
- `DELETE /api/profiles/{name}` removes the temporary test profile
