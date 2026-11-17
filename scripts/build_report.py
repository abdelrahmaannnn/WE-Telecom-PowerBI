import json, os, shutil, sys

REPORT = r"C:\Users\owner\Downloads\WE_DATA_Power_Bi.Report"
ASSETS = r"C:\Users\owner\Downloads\WE_assets"
DEF = os.path.join(REPORT, "definition")
PAGES = os.path.join(DEF, "pages")
DASH = "26883dbcdc08d399af48"
HOME = "home"
NET = "network"
VSCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json"
PSCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
IMGS = {"home_bg.png": "home_bg.png", "dashboard_bg.png": "dashboard_bg.png", "network_bg.png": "network_bg.png", "we_logo.png": "we_logo.png"}


def lit(v):
    if isinstance(v, bool):
        s = "true" if v else "false"
    elif isinstance(v, (int, float)):
        s = f"{v}D"
    else:
        s = "'" + str(v).replace("'", "''") + "'"
    return {"expr": {"Literal": {"Value": s}}}


def color(hex_):
    return {"solid": {"color": lit(hex_)}}


def props(**kw):
    out = {}
    for k, v in kw.items():
        out[k] = color(v[1:]) if isinstance(v, str) and v.startswith("c#") else lit(v)
    return [{"properties": out}]


def measure(name, table="Measure"):
    return {"Measure": {"Expression": {"SourceRef": {"Entity": table}}, "Property": name}}


def column(table, name):
    return {"Column": {"Expression": {"SourceRef": {"Entity": table}}, "Property": name}}


def proj(field):
    ent = list(field.values())[0]
    ref = f'{ent["Expression"]["SourceRef"]["Entity"]}.{ent["Property"]}'
    return {"field": field, "queryRef": ref, "nativeQueryRef": ent["Property"]}


def container(title=None, title_color="#3E1F5C"):
    o = {
        "background": props(show=False),
        "border": props(show=False),
        "dropShadow": props(show=False),
        "title": props(show=False),
    }
    if title:
        o["title"] = props(show=True, text=title, fontColor="c" + title_color, fontSize=13, bold=True,
                           fontFamily="Segoe UI Semibold")
    return o


def visual(page, name, x, y, w, h, z, vtype, query=None, objects=None, vco=None, sort=None, extra=None):
    v = {"visualType": vtype}
    if query:
        v["query"] = {"queryState": query}
        if sort:
            v["query"]["sortDefinition"] = {"sort": sort, "isDefaultSort": False}
    if objects:
        v["objects"] = objects
    v["visualContainerObjects"] = vco if vco is not None else container()
    v["drillFilterOtherVisuals"] = True
    doc = {"$schema": VSCHEMA, "name": name,
           "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z},
           "visual": v}
    if extra:
        doc.update(extra)
    d = os.path.join(PAGES, page, "visuals", name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "visual.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)


def card(page, name, x, y, w, h, z, m, value_color, label_color, size=20):
    visual(page, name, x, y, w, h, z, "card",
           query={"Values": {"projections": [proj(measure(m))]}},
           objects={"labels": props(color="c" + value_color, fontSize=size, fontFamily="Segoe UI Semibold"),
                    "categoryLabels": props(show=True, color="c" + label_color, fontSize=10)},
           vco={**container(), "padding": [{"properties": {"top": lit(0), "bottom": lit(0), "left": lit(0), "right": lit(0)}}]})


def nav_button(page, name, x, y, w, h, z, target, tooltip):
    visual(page, name, x, y, w, h, z, "actionButton",
           objects={"icon": [{"properties": {"shapeType": lit("blank")}, "selector": {"id": "default"}}],
                    "fill": [{"properties": {"show": lit(False)}, "selector": {"id": "default"}}],
                    "outline": [{"properties": {"show": lit(False)}, "selector": {"id": "default"}}],
                    "text": [{"properties": {"show": lit(False)}, "selector": {"id": "default"}}]},
           vco={**container(), "visualLink": [{"properties": {
               "show": lit(True), "type": lit("PageNavigation"),
               "navigationSection": lit(target), "tooltip": lit(tooltip)}}]},
           extra={"howCreated": "InsertVisualButton"})


def page_json(name, display, bg):
    return {"$schema": PSCHEMA, "name": name, "displayName": display, "displayOption": "FitToPage",
            "height": 720, "width": 1280,
            "objects": {
                "background": [{"properties": {
                    "image": {"image": {
                        "name": lit(bg),
                        "url": {"expr": {"ResourcePackageItem": {"PackageName": "RegisteredResources",
                                                                 "PackageType": 1, "ItemName": IMGS[bg]}}},
                        "scaling": lit("Fit")}},
                    "transparency": lit(0)}}],
                "outspace": [{"properties": {"color": color("#1E0833" if name == HOME else "#F4F1F8")}}]}}


# ---------- resources ----------
rr = os.path.join(REPORT, "StaticResources", "RegisteredResources")
os.makedirs(rr, exist_ok=True)
for src, dst in IMGS.items():
    shutil.copy(os.path.join(ASSETS, src), os.path.join(rr, dst))

theme = {
    "name": "WE Purple",
    "dataColors": ["#6B2C91", "#C13B9A", "#E78AC3", "#8E7CC3", "#3E1F5C", "#F2A1D0", "#5E8DE0", "#F7B267"],
    "background": "#FFFFFF", "foreground": "#2B1840", "tableAccent": "#8E2A8C",
    "good": "#2E9E6B", "bad": "#C8364F", "neutral": "#8E7CC3",
    "textClasses": {
        "label": {"fontFace": "Segoe UI", "color": "#5A4A6B", "fontSize": 9},
        "title": {"fontFace": "Segoe UI Semibold", "color": "#3E1F5C", "fontSize": 12},
        "callout": {"fontFace": "Segoe UI Semibold", "color": "#2B1840"},
    },
    "visualStyles": {"*": {"*": {
        "background": [{"show": False}],
        "border": [{"show": False}],
        "dropShadow": [{"show": False}],
    }}},
}
with open(os.path.join(rr, "WE_Purple.json"), "w", encoding="utf-8") as f:
    json.dump(theme, f, indent=2)

rp = os.path.join(DEF, "report.json")
rep = json.load(open(rp, encoding="utf-8"))
rep["resourcePackages"] = [p for p in rep["resourcePackages"] if p["name"] != "RegisteredResources"]
rep["resourcePackages"].append({"name": "RegisteredResources", "type": "RegisteredResources", "items":
    [{"name": n, "path": n, "type": "Image"} for n in IMGS.values()] +
    [{"name": "WE_Purple.json", "path": "WE_Purple.json", "type": "CustomTheme"}]})
rep["themeCollection"]["customTheme"] = {"name": "WE_Purple.json",
                                         "reportVersionAtImport": rep["themeCollection"]["baseTheme"]["reportVersionAtImport"],
                                         "type": "RegisteredResources"}
json.dump(rep, open(rp, "w", encoding="utf-8"), indent=2)

# ---------- pages ----------
shutil.rmtree(os.path.join(PAGES, DASH, "visuals"), ignore_errors=True)
shutil.rmtree(os.path.join(PAGES, HOME), ignore_errors=True)
shutil.rmtree(os.path.join(PAGES, NET), ignore_errors=True)
os.makedirs(os.path.join(PAGES, NET, "visuals"))
json.dump(page_json(NET, "Network & Experience", "network_bg.png"), open(os.path.join(PAGES, NET, "page.json"), "w", encoding="utf-8"), indent=2)
os.makedirs(os.path.join(PAGES, HOME, "visuals"))
json.dump(page_json(HOME, "Home", "home_bg.png"), open(os.path.join(PAGES, HOME, "page.json"), "w", encoding="utf-8"), indent=2)
json.dump(page_json(DASH, "Dashboard", "dashboard_bg.png"), open(os.path.join(PAGES, DASH, "page.json"), "w", encoding="utf-8"), indent=2)
json.dump({"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
           "pageOrder": [HOME, DASH, NET], "activePageName": HOME},
          open(os.path.join(PAGES, "pages.json"), "w", encoding="utf-8"), indent=2)

# ---------- HOME visuals ----------
for i, (x, m) in enumerate([(450, "Total Revenue"), (695, "Active Customers"), (940, "Network Availability %")]):
    card(HOME, f"home_kpi_{i}", x + 66, 300, 156, 88, i, m, "#FFFFFF", "#F2C6E6", 24)
nav_button(HOME, "home_nav_dashboard", 450, 430, 270, 56, 10, DASH, "Revenue & Customers")
nav_button(HOME, "home_nav_network", 740, 430, 270, 56, 11, NET, "Network & Experience")

# ---------- DASHBOARD visuals ----------
z = 0
def year_slicer(page, name, z):
  visual(page, name, 960, 17, 186, 30, z, "slicer",
       query={"Values": {"projections": [proj(column("Dim_Date", "Year"))]}},
       objects={"data": props(mode="Dropdown"),
                "header": props(show=False),
                "items": props(fontColor="c#3E1F5C", textSize=10)})
year_slicer(DASH, "dash_year_slicer", z); z += 1
nav_button(DASH, "dash_nav_network", 806, 16, 136, 32, z, NET, "Network & Experience"); z += 1
nav_button(DASH, "dash_nav_home", 1162, 16, 102, 32, z, HOME, "Back to Home"); z += 1

kpis = ["Total Revenue", "Gross Profit", "Gross Margin %", "ARPU", "Active Customers", "Churn Rate"]
for i, m in enumerate(kpis):
    x = 16 + i * 209.8
    card(DASH, f"dash_kpi_{i}", round(x + 64, 1), 84, 130, 84, z, m, "#2B1840", "#7A6A8C"); z += 1

ym = column("Dim_Date", "Year Month")
visual(DASH, "dash_rev_arpu_trend", 24, 190, 764, 258, z, "lineClusteredColumnComboChart",
       query={"Category": {"projections": [{**proj(ym), "active": True}]},
              "Y": {"projections": [proj(measure("Total Revenue"))]},
              "Y2": {"projections": [proj(measure("ARPU"))]}},
       sort=[{"field": ym, "direction": "Ascending"}],
       objects={"lineStyles": props(strokeWidth=3),
                "legend": props(show=True, position="TopRight"),
                "categoryAxis": props(showAxisTitle=False),
                "valueAxis": props(showAxisTitle=False, gridlineShow=False)},
       vco=container("Revenue & ARPU Trend")); z += 1

visual(DASH, "dash_rev_region", 814, 190, 442, 258, z, "donutChart",
       query={"Category": {"projections": [proj(column("Dim_Geography", "Region"))]},
              "Y": {"projections": [proj(measure("Total Revenue"))]}},
       objects={"legend": props(show=True, position="Right"),
                "labels": props(labelStyle="Percent of total")},
       vco=container("Revenue by Region")); z += 1

visual(DASH, "dash_rev_plan", 24, 466, 394, 238, z, "clusteredBarChart",
       query={"Category": {"projections": [proj(column("Dim_Plan", "Plan_Name"))]},
              "Y": {"projections": [proj(measure("Total Revenue"))]}},
       sort=[{"field": measure("Total Revenue"), "direction": "Descending"}],
       objects={"labels": props(show=True, labelDisplayUnits=1000000, fontSize=8),
                "valueAxis": props(show=False, showAxisTitle=False),
                "categoryAxis": props(showAxisTitle=False, fontSize=8)},
       vco=container("Revenue by Plan (M)")); z += 1

visual(DASH, "dash_churn_segment", 444, 466, 394, 238, z, "clusteredColumnChart",
       query={"Category": {"projections": [proj(column("Dim_Customer", "Segment"))]},
              "Y": {"projections": [proj(measure("Churn Rate"))]}},
       objects={"labels": props(show=True),
                "dataPoint": props(fillColor="c#C13B9A"),
                "valueAxis": props(show=False, showAxisTitle=False),
                "categoryAxis": props(showAxisTitle=False)},
       vco=container("Churn Rate by Segment")); z += 1

visual(DASH, "dash_region_table", 864, 466, 392, 238, z, "tableEx",
       query={"Values": {"projections": [proj(column("Dim_Geography", "Region")), proj(measure("Total Revenue")),
                                          proj(measure("Gross Margin %")), proj(measure("ARPU")),
                                          proj(measure("Churn Rate"))]}},
       objects={"columnHeaders": props(fontColor="c#FFFFFF", backColor="c#5B1F86", fontSize=10),
                "values": props(fontSize=10, backColorPrimary="c#FFFFFF", backColorSecondary="c#F7F2FA"),
                "total": props(fontColor="c#3E1F5C", backColor="c#EFE6F5"),
                "grid": props(gridHorizontal=False, gridVertical=False)},
       vco=container("Regional Summary")); z += 1


# ---------- NETWORK & EXPERIENCE page ----------
z = 0
year_slicer(NET, "net_year_slicer", z); z += 1
nav_button(NET, "net_nav_dashboard", 806, 16, 136, 32, z, DASH, "Revenue & Customers"); z += 1
nav_button(NET, "net_nav_home", 1162, 16, 102, 32, z, HOME, "Back to Home"); z += 1
for i, m in enumerate(["Network Availability %", "Dropped Call Rate", "Total Calls", "Average NPS Score",
                       "Average CSAT Score", "First Contact Resolution Rate"]):
    x = 16 + i * 209.8
    card(NET, f"net_kpi_{i}", round(x + 64, 1), 84, 130, 84, z, m, "#2B1840", "#7A6A8C"); z += 1

visual(NET, "net_drop_trend", 24, 190, 764, 258, z, "lineChart",
       query={"Category": {"projections": [{**proj(ym), "active": True}]},
              "Y": {"projections": [proj(measure("Dropped Call Rate"))]},
              "Y2": {"projections": [proj(measure("Network Availability %"))]}},
       sort=[{"field": ym, "direction": "Ascending"}],
       objects={"lineStyles": props(strokeWidth=3, showMarker=True),
                "legend": props(show=True, position="TopRight"),
                "categoryAxis": props(showAxisTitle=False),
                "valueAxis": props(showAxisTitle=False, gridlineShow=False, secShowAxisTitle=False)},
       vco=container("Dropped Call Rate vs Network Availability")); z += 1

visual(NET, "net_avail_region", 814, 190, 442, 258, z, "clusteredBarChart",
       query={"Category": {"projections": [proj(column("Dim_Geography", "Region"))]},
              "Y": {"projections": [proj(measure("Total Dropped Calls"))]}},
       sort=[{"field": measure("Total Dropped Calls"), "direction": "Descending"}],
       objects={"labels": props(show=True),
                "dataPoint": props(fillColor="c#C13B9A"),
                "valueAxis": props(show=False, showAxisTitle=False),
                "categoryAxis": props(showAxisTitle=False)},
       vco=container("Dropped Calls by Region")); z += 1

visual(NET, "net_csat_interaction", 24, 466, 394, 238, z, "clusteredColumnChart",
       query={"Category": {"projections": [proj(column("Fact_Experience", "Interaction_Type"))]},
              "Y": {"projections": [proj(measure("Average CSAT Score")), proj(measure("Average NPS Score"))]}},
       objects={"labels": props(show=True, fontSize=8),
                "legend": props(show=True, position="TopRight"),
                "valueAxis": props(show=False, showAxisTitle=False),
                "categoryAxis": props(showAxisTitle=False)},
       vco=container("CSAT & NPS by Interaction Type")); z += 1

visual(NET, "net_new_by_channel", 444, 466, 394, 238, z, "donutChart",
       query={"Category": {"projections": [proj(column("Dim_Channel", "Channel_Name"))]},
              "Y": {"projections": [proj(measure("Total New Customers"))]}},
       objects={"legend": props(show=True, position="Right"),
                "labels": props(labelStyle="Percent of total")},
       vco=container("New Customers by Channel")); z += 1

visual(NET, "net_cac_channel", 864, 466, 392, 238, z, "clusteredBarChart",
       query={"Category": {"projections": [proj(column("Dim_Channel", "Channel_Name"))]},
              "Y": {"projections": [proj(measure("Customer Acquisition Cost"))]}},
       sort=[{"field": measure("Customer Acquisition Cost"), "direction": "Descending"}],
       objects={"labels": props(show=True),
                "valueAxis": props(show=False, showAxisTitle=False),
                "categoryAxis": props(showAxisTitle=False)},
       vco=container("Acquisition Cost by Channel")); z += 1
print("built all pages")
