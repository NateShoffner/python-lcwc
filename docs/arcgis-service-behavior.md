# ArcGIS live feed service behavior

Notes on how the upstream ArcGIS service actually behaves, why `ArcGISClient`
queries each layer twice, and which gaps are outside the client's control.

Measured 2026-08-11 over a 90 minute window, 180 samples at 30 second
intervals, comparing `ArcGISClient`, `FeedClient` and `WebClient` side by side.
18 distinct incidents passed through, covering all three layers.

## The service

```
https://utility.arcgis.com/usrsvcs/servers/a1f6aa7faab44b1582029509c46dce86
    /rest/services/Maps/Public_LiveFeeds/MapServer
```

Three point layers, `maxRecordCount` 2000, no definition expression, no time
info:

| Layer | Name              | Category  |
| ----- | ----------------- | --------- |
| 0     | Fire Incidents    | `FIRE`    |
| 1     | EMS Incidents     | `MEDICAL` |
| 2     | Traffic Incidents | `TRAFFIC` |

This is the same service the official LCWC live map consumes. The map at
`lcwc911.us/live-incident-map` embeds web app `cc2eb34d14ce4f2ba15e1f1a3ccb6a01`,
whose web map `5b0e126547b046e69e9559ea866bdf34` lists exactly this MapServer as
its `Live Incidents` operational layer with a 30 second refresh. There is no
richer or alternate endpoint to fall back on, which is why gaps in this service
show up identically on the official map.

## Requesting geometry silently drops rows

This is the root cause of [#3](https://github.com/NateShoffner/python-lcwc/issues/3).

The service routinely holds rows whose geometry is null, because the address has
not been geocoded yet or never will be. **Any query that asks for geometry drops
those rows without comment**, and a spatial filter implies one. Same layer, same
instant, only the output flags varying:

```
geom=false=4   geom=true=2   geom=true,outSR=4326=2   countOnly=4
```

`returnCountOnly` and `returnGeometry=false` agree on 4. Asking for geometry
returns 2. Identifying the rows that vanish:

```
OK   oid=4 2608012247 WEST LAMPETER TOWNSHIP  geom={'x': -8490111.67, 'y': 4863072.28}
OK   oid=5 2608012253 CLAY TOWNSHIP           geom={'x': -8487468.24, 'y': 4897429.80}
DROP oid=6 2608012253 CLAY TOWNSHIP
DROP oid=7 2608012270 MANHEIM BOROUGH | E HIGH ST / S HAZEL ST
```

The dropped rows carry no geometry at all: `returnExtentOnly=true` on either one
returns `{"xmin": "NaN", "ymin": "NaN", "xmax": "NaN", "ymax": "NaN"}`. They are
unreachable through every output variant tried, including `f=geojson`,
`returnCentroid=true`, `outSR=102100`, `geometryPrecision` and quantization.
Normally a null-geometry feature comes back as `"geometry": null`; this service
omits the row entirely.

Manheim Borough above had no geocoded twin, so that incident was invisible to any
geometry-bearing query.

**The spatial envelope was never the problem.** `returnGeometry=true` with no
spatial filter whatsoever still returns the reduced set, so widening the
envelope, splitting the county into quadrants, or dropping the filter changes
nothing. The envelope has been removed because `where=1=1` alone already returns
every row the service holds, and the filter could only ever subtract.

Geometry also flaps. Clay Township had coordinates at 23:51 and none at 23:55,
so a row that answers a geometry query now may not answer the next one.

### How the client works around it

Each layer is queried twice: once with `returnGeometry=false` for the
authoritative row set, once with `returnGeometry=true` purely as a coordinate
lookup keyed on `IncidentNumber`. Incidents come from the first query, so nothing
is lost; coordinates are attached when the second query has them.

`ArcGISIncident.coordinates` is therefore `Optional[Coordinates]`. Over the
measurement window the client returned coordinates for 741 of 775 incidents
(96%).

## Duplicate rows

The service sometimes carries more than one row for a single incident, typically
one geocoded and one not (`oid=5` and `oid=6` above are both incident
2608012253, identical in every attribute). The client dedupes on
`IncidentNumber` per layer.

Duplicate and null-geometry rows appeared in 26 of 180 samples, clustered in
bursts rather than spread evenly. Across the window a geometry-bearing query
would have dropped 4.7% of rows on average, and 50% in the worst sample.

## Incidents the service never publishes

Four incidents in the window never appeared in the service at any point in their
lifetimes, across every sample the feed carried them:

```
[NEVER] 150/150  EAST LAMPETER|LANDIS AVE + LINCOLN HWY E   ROUTINE TRANSFER-CLASS 3
[NEVER]   99/99  ELIZABETH|HOPELAND RD + LEE LN             ROUTINE TRANSFER-CLASS 3
[NEVER]   40/40  QUARRYVILLE|PARK AVE + S HESS ST           EMS ACTIVITY
[NEVER]   30/30  FULTON|ROBERT FULTON HWY + WARFEL RD       ROUTINE TRANSFER-CLASS 3
```

Only two types, `ROUTINE TRANSFER-CLASS 3` and `EMS ACTIVITY`. Every
emergency-type incident reached the service, including fire and traffic. This
looks like a deliberate upstream filter on the public map rather than a defect,
and no client-side change can recover them. Callers who need complete coverage
of non-emergency EMS activity should use `FeedClient` or `WebClient`.

## Timing and transient dropouts

Aggregated over the 14 incidents that did reach the service, 790 samples of
lifetime:

| Behavior                                        | Measurement           |
| ----------------------------------------------- | --------------------- |
| Ingest lag before the service picks an incident up | ~19s                |
| Trailing presence after the feed clears it      | ~13s                  |
| Mid-lifetime single-sample dropouts             | 6 (0.76% of samples)  |

The dropouts are the notable one. An incident the service is already carrying can
vanish for a single poll and return on the next, presumably during the same table
rebuild that produces the empty-layer blips below. Rendering two incident
lifetimes at 30s per character, `F` = feed only, `B` = both, `A` = ArcGIS only:

```
LANCASTER|CHESTER ST + S DUKE ST   FBFBBBBBBBBBBB...BBBBFBBBBBB...BBBBA
EAST PETERSBURG|SUNDRA CIR         FBBBBBBBBBBBBB...BBBBFBBBBBB...BBBBB
```

A consumer diffing consecutive polls will see spurious clear/re-open pairs at
roughly 1 sample in 130. Debouncing by one poll suppresses it. The client does
not do this, because a genuine clear-down is indistinguishable from a dropout
within a single sample and the delay would be paid on every incident.

Separately, the whole layer occasionally returns zero rows mid-refresh: 2 of 151
samples in an earlier 6 minute run at 2 second intervals, 0 of 180 in the 90
minute run. A poller can misread that as "all incidents cleared". A retry on
empty would mask it, but zero is also legitimate during quiet hours, so the
client does not retry.

## Unrelated: the feed client drops MICU units

Found while cross-checking the three clients, not an ArcGIS issue.

`MEDICAL_UNIT_NAMES` in `src/lcwc/feed/utils/__init__.py` is
`["AMB", "EMS", "INT", "MEDIC", "QRS"]`. `MICU` is missing, and that one omission
causes two failures, because the list gates both `has_unit_names()` in
`feed/parser.py` and `determine_category()`:

1. The units segment is not recognized as units, so `unit_names` stays empty and
   the MICU unit is discarded entirely.
2. With no units, classification falls through to the description keyword check,
   which only matches `MEDICAL`. `EMS ACTIVITY` and `ROUTINE TRANSFER-CLASS 3`
   therefore land in `UNKNOWN`.

Same instant, same incidents:

```
FEED:  UNKNOWN  QUARRYVILLE BOROUGH   units=[]        EMS ACTIVITY
       MEDICAL  CLAY TOWNSHIP         units=[]        MEDICAL EMERGENCY
       UNKNOWN  FULTON TOWNSHIP       units=[]        ROUTINE TRANSFER-CLASS 3
WEB:   MEDICAL  Quarryville Borough   units=['MICU']  EMS ACTIVITY
       MEDICAL  Clay Township         units=['MICU']  MEDICAL EMERGENCY
       MEDICAL  Fulton Township       units=['MICU']  ROUTINE TRANSFER-CLASS 3
```

Clay Township got `MEDICAL` only because its description happened to say so,
which masks the unit loss. The raw feed confirms the units are present upstream:
`QUARRYVILLE BOROUGH;  PARK AVE & S HESS ST; MICU 56-5;`.

`WebClient` is immune because it reads the category from the page's section
header instead of inferring it. `UnitParser` handles `MICU` fine, so the keyword
list is the only gate. This was observed across 169 samples and is not fixed.

## Feed and web agree

`FeedClient` and `WebClient` returned identical incident sets in 180 of 180
samples. The only differences between them are the categories above.

## Reproducing

Incidents are matched across sources by normalized location, since the three
sources share no identifier: the feed has a guid, the web page has nothing, and
ArcGIS has `IncidentNumber`. Two genuinely distinct co-located incidents (a
structure fire and its EMS dispatch, filed as separate CAD incidents at one
address) therefore collapse into a single key. This happened in about 10 of 180
samples and is a limitation of any cross-source comparison, not of the clients.

The quickest way to observe the core defect directly:

```
GET .../MapServer/1/query?f=json&where=1=1&returnCountOnly=true
GET .../MapServer/1/query?f=json&where=1=1&outFields=IncidentNumber&returnGeometry=false
GET .../MapServer/1/query?f=json&where=1=1&outFields=IncidentNumber&returnGeometry=true
```

Whenever the third disagrees with the first two, the difference is rows the
service holds but will not hand over with geometry attached.
