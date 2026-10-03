"""Shared Annual KPI presentation model for the existing XLSX/Sheets writers.

No source calculations live here. Blank and MANUAL values stay unavailable.
Completed-year Upto and selected-year YTD are labelled as different periods.
"""
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import math
from report_branding import LOGO_URL, add_logo

NAVY = "12345B"
BLUE = "1976B9"
GREEN = "287B59"
ORANGE = "B66521"
PURPLE = "7056A5"
INK = "23364D"
PALE = "F3F6FA"
LINE = "CCD7E3"
FY_COLORS = ("EAF2FA", "EAF4EE", "FFF2D9")


def number(value):
    if value is None or value == "" or isinstance(value, bool): return None
    if isinstance(value, (int, float)): return value if math.isfinite(value) else None
    try:
        result = float(str(value).replace(",", ""))
        return result if math.isfinite(result) else None
    except ValueError: return None


def records(mat, fys):
    """Read labels even when Sheets omits trailing blank cells."""
    result = {}; name = ""
    for raw in mat:
        row = list(raw) + [""] * max(0, 18-len(raw))
        if str(row[2]) not in fys: continue
        if str(row[1] or "").strip(): name = str(row[1]).strip()
        if name: result.setdefault(name, {})[str(row[2])] = row
    return result


def group(name):
    if name.startswith("HSD"): return "Fuel efficiency (KMPL)", BLUE
    if name.startswith("PRODUCT:"): return "Product KMPL", GREEN
    if name.startswith("ENGINE:"): return "Engine KMPL", ORANGE
    if name in {"AVG TYRE LIFE", "NEW TYRE LIFE", "RC TYRE LIFE", "N.T.S RATE", "Ist RC S Rate", "TTL SCP Rate", "RT Factor"}:
        return "Tyre performance", PURPLE
    return "Other operating KPIs", NAVY


def period_label(selected):
    return datetime.strptime(selected, "%Y-%m").strftime("%B %Y")


# Rates retain the original APSRTC units; do not multiply by 100.
KPI_FORMATS = {"B.D RATE": "0.0000", "MED CANCL.": "0.0000"}
GOOD, BAD, NEUTRAL = "146B58", "A33232", "526174"


def kpi_format(name):
    return KPI_FORMATS.get(name, "0.00")


def target_status(name, value, target):
    if value is None: return "UNAVAILABLE", NEUTRAL
    eligible = name.startswith("HSD") or name in {"TOTAL LUB KMPL", "B.D RATE", "MED CANCL."}
    if target is None or not eligible: return "NO TARGET", NEUTRAL
    lower = name in {"B.D RATE", "MED CANCL."}
    good = value <= target if lower else value >= target
    if value == target: return "ON TARGET", GOOD
    return ("ON TARGET" if good else "BELOW TARGET"), (GOOD if good else BAD)


def target_delta(name, value, target):
    if value is None or target is None: return "Source target unavailable"
    precision = 4 if kpi_format(name) == "0.0000" else 2
    delta = Decimal(str(value))-Decimal(str(target))
    shown = delta.quantize(Decimal(1).scaleb(-precision), rounding=ROUND_HALF_UP)
    return f"{shown:+.{precision}f} vs target {target:.{precision}f}"


def dashboard_model(display, fys, mat, selected):
    data = records(mat, fys)
    # Equal card widths with three true gutters; source columns remain hidden.
    model = {"cells": [], "widths": [78]*19+[78]*5, "charts": [],
             "height": 23, "last_row": 52,
             "anchors": {"hero": [], "summary": {}, "chart_sources": []}}
    def cell(r,c,text,rs=1,cs=1,fill="FFFFFF",color=INK,size=10,bold=False,align="left",fmt="General"):
        model["cells"].append(dict(r=r,c=c,text=text,rs=rs,cs=cs,fill=fill,color=color,size=size,bold=bold,align=align,fmt=fmt))
    period = period_label(selected); current = fys[-1]
    endmon = datetime.strptime(selected, "%Y-%m").strftime("%b")
    cell(0,0,"APSRTC  ANNUAL KPI",cs=13,fill=NAVY,color="FFFFFF",size=20,bold=True)
    cell(1,0,f"{display} DEPOT    Reporting through {period}",cs=13,size=14,bold=True)
    cell(2,0,f"FY {fys[0]} and {fys[1]}: full-year Upto     FY {current}: April–{endmon} YTD",cs=19,size=10)
    cards=[("HSD KMPL INCL AC","HSD INCL. AC · YTD KMPL",BLUE),
           ("HSD KMPL EXCL AC","HSD EXCL. AC · YTD KMPL",BLUE),
           ("AVG TYRE LIFE","AVG TYRE LIFE · LAKH KM",PURPLE),
           ("B.D RATE","BREAKDOWN RATE · YTD",ORANGE)]
    for i,(key,label,color) in enumerate(cards):
        col=i*5; row=data.get(key,{}).get(current,[""]*18)
        val, target = number(row[17]), number(row[3])
        status, semantic = target_status(key,val,target)
        model["anchors"]["hero"].append(dict(kpi=key,label=[4,col],value=[5,col],status=[7,col],delta=[8,col],caption=[9,col]))
        cell(4,col,label,cs=4,fill=color,color="FFFFFF",bold=True,size=10)
        cell(5,col,"—" if val is None else val,rs=2,cs=4,fill=PALE,color=semantic,size=20,bold=True,align="center",fmt=kpi_format(key))
        cell(7,col,status,cs=4,fill=PALE,color=semantic,bold=True,align="center",size=10)
        cell(8,col,target_delta(key,val,target),cs=4,fill=PALE,size=9,align="center")
        cell(9,col,f"FY {current} · Apr–{endmon}",cs=4,fill=PALE,size=9,align="center")
    cell(11,0,"KPI summary",cs=10,size=13,bold=True)
    cell(12,0,"KPI / parameter",cs=4,fill=NAVY,color="FFFFFF",bold=True)
    for c,label in [(4,"Target"),(5,fys[0]+" Full FY"),(6,fys[1]+" Full FY"),(7,current+" YTD"),(8,"Δ vs target"),(9,"YTD status")]:
        cell(12,c,label,fill=NAVY,color="FFFFFF",bold=True,align="center",size=9)
    missing_engines=[]; previous=None; r=13
    for name, years in data.items():
        current_row=years.get(current,[""]*18)
        val=number(current_row[17]); target=number(current_row[3])
        if name.startswith("ENGINE:") and val is None:
            missing_engines.append(name); continue
        title,color=group(name)
        if title!=previous:
            cell(r,0,title,cs=10,fill=color,color="FFFFFF",bold=True); r+=1; previous=title
        model["anchors"]["summary"][name]=[r,0]
        label=name.replace("PRODUCT: ","").replace("ENGINE: ","")
        if name in {"AVG TYRE LIFE","NEW TYRE LIFE","RC TYRE LIFE"}: label += " (lakh km)"
        fill=PALE if r%2==0 else "FFFFFF"
        cell(r,0,label,cs=4,fill=fill)
        cell(r,4,target if target is not None else "—",fill=fill,align="right",fmt=kpi_format(name))
        for j,fy in enumerate(fys):
            value=number(years.get(fy,[""]*18)[17])
            fy_status,_=target_status(name,value,number(years.get(fy,[""]*18)[3]))
            value_fill={"ON TARGET":"E2F0D9", "BELOW TARGET":"F4CCCC", "UNAVAILABLE":PALE}.get(fy_status,FY_COLORS[j])
            cell(r,5+j,value if value is not None else "—",fill=value_fill,bold=(j==2),align="right",fmt=kpi_format(name))
        status,semantic=target_status(name,val,target)
        graded=status in ("ON TARGET","BELOW TARGET")
        cell(r,8,val-target if graded else "—",fill=fill,align="right",fmt=kpi_format(name))
        cell(r,9,{"ON TARGET":"MET", "BELOW TARGET":"BELOW", "NO TARGET":"—", "UNAVAILABLE":"—"}[status],fill=fill,color=semantic,bold=graded,size=8,align="center")
        r+=1
    sy,sm=map(int,selected.split("-")); count=(sm-4)%12+1
    months=["Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec","Jan","Feb","Mar"][:count]
    for idx,(title,keys,labels,unit) in enumerate([
        ("Monthly HSD KMPL",["HSD KMPL INCL AC","HSD KMPL EXCL AC"],["Incl. AC","Excl. AC"],"KMPL"),
        ("Monthly tyre life",["AVG TYRE LIFE","NEW TYRE LIFE","RC TYRE LIFE"],["Average","New","RC"],"lakh km")]):
        hr=idx*16; cell(hr,19,"Month"); series=[]
        for j,(key,label) in enumerate(zip(keys,labels)):
            series.append(dict(key=key,label=label,target=False))
        if idx==0:
            for key,label in zip(keys,labels):
                target=number(data.get(key,{}).get(current,[""]*18)[3])
                if target is not None: series.append(dict(key=key,label=label+" target",target=True,value=target))
        for j,ser in enumerate(series,20): cell(hr,j,ser["label"])
        for mi,mon in enumerate(months):
            cell(hr+mi+1,19,mon)
            for j,ser in enumerate(series,20):
                source=data.get(ser['key'],{}).get(current,[""]*18)
                cell(hr+mi+1,j,ser['value'] if ser['target'] else number(source[4+mi]),fmt="0.00")
        model["anchors"]["chart_sources"].append([hr,19])
        model["charts"].append(dict(title=f"{title} — FY {current}",unit=unit,
            source_row=hr,points=count,series=len(series),labels=[x['label'] for x in series],
            targets=[x['target'] for x in series],row=12+idx*16,col=11,width=624,height=300))
    note=max(r+1,46)
    if missing_engines:
        cell(note,0,f"{len(missing_engines)} engine rows have no YTD source value. Exact labels and history remain in Detailed Data.",cs=19,size=10); note+=1
    cell(note,0,"— = missing source value; not zero. Full-year and YTD totals are not like-for-like comparisons.",cs=19,size=10)
    cell(note+1,0,"Tyre life: lakh km. Rates retain APSRTC units. Charts stop at the selected month; KMPL axis is not zero-based.",cs=19,size=10)
    cell(note+2,0,"Fuel/lubricant KMPL: higher is better. BD/MED: lower is better. MET/BELOW use source targets only.",cs=19,size=10)
    model["last_row"]=note+3
    return model


def render_xlsx_dashboard(wb,title,model,display,selected):
    # Integrates with the repository's established openpyxl report writer.
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.chart import LineChart, Reference
    from openpyxl.chart.series import SeriesLabel
    from openpyxl.utils import get_column_letter
    if title in wb.sheetnames: del wb[title]
    ws=wb.create_sheet(title,0); ws.sheet_view.showGridLines=False
    for i,width in enumerate(model["widths"],1): ws.column_dimensions[get_column_letter(i)].width=(width-5)/7
    for r in range(1,model["last_row"]+1): ws.row_dimensions[r].height=model["height"]*.75
    ws.row_dimensions[13].height=32
    ws.freeze_panes="A4"
    ws.row_dimensions[1].height=34; ws.row_dimensions[2].height=26
    for spec in model["cells"]:
        r,c=spec["r"]+1,spec["c"]+1; er,ec=r+spec["rs"]-1,c+spec["cs"]-1
        if er>r or ec>c: ws.merge_cells(start_row=r,start_column=c,end_row=er,end_column=ec)
        for row in ws.iter_rows(min_row=r,max_row=er,min_col=c,max_col=ec):
            for v in row: v.fill=PatternFill("solid",fgColor=spec["fill"])
        v=ws.cell(r,c,spec["text"])
        v.font=Font(name="Arial",size=spec["size"],bold=spec["bold"],color=spec["color"])
        v.alignment=Alignment(horizontal=spec["align"],vertical="center",wrap_text=True)
        v.number_format=spec.get("fmt", "General")
        if 11<=spec["r"]<model["last_row"]-2 and spec["c"]<7:
            v.border=Border(bottom=Side(style="hair",color=LINE))
    for spec in model["charts"]:
        chart=LineChart(); chart.title=spec["title"]; chart.y_axis.title=spec["unit"]
        chart.style=13; chart.height=spec["height"]*.0264583; chart.width=spec["width"]*.0264583; chart.display_blanks="gap"
        chart.smooth=False
        chart.y_axis.numFmt="0.00"
        chart.visible_cells_only=False
        start=spec["source_row"]+1
        chart.add_data(Reference(ws,min_col=21,max_col=20+spec["series"],min_row=start,max_row=start+spec["points"]),titles_from_data=True)
        chart.set_categories(Reference(ws,min_col=20,min_row=start+1,max_row=start+spec["points"]))
        chart.legend.position="b"
        # Explicit titles keep Excel/LibreOffice and preview renderers from
        # falling back to generic "Series 1" labels.
        for i,(ser,label) in enumerate(zip(chart.series,spec.get("labels",[]))):
            color=[BLUE,GREEN,ORANGE,NEUTRAL][i%4]
            ser.smooth=False
            ser.marker.symbol="none" if spec["targets"][i] else "circle"
            ser.marker.size=4
            ser.tx=SeriesLabel(v=label)
            ser.graphicalProperties.line.solidFill=color
            ser.graphicalProperties.line.width=24000
            if spec.get("targets",[])[i]: ser.graphicalProperties.line.prstDash="dash"
        ws.add_chart(chart,f"{get_column_letter(spec['col']+1)}{spec['row']+1}")
    for col in range(20,25): ws.column_dimensions[get_column_letter(col)].hidden=True
    add_logo(ws, "O1", width=300)
    print_setup(ws,display,period_label(selected),"1:3",19,model["last_row"],one_page=True)
    return ws


def print_setup(ws,display,period,repeat,last_col,last_row,one_page=False):
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.page import PageMargins
    from openpyxl.worksheet.properties import PageSetupProperties
    ws.print_title_rows=repeat
    ws.print_area=f"A1:{get_column_letter(last_col)}{last_row}"
    ws.page_setup.orientation="landscape"
    ws.page_setup.paperSize=ws.PAPERSIZE_A3
    ws.page_setup.fitToWidth=1
    ws.page_setup.fitToHeight=1 if one_page else 0
    ws.page_setup.scale=None
    ws.sheet_properties.pageSetUpPr=PageSetupProperties(fitToPage=True,autoPageBreaks=False)
    ws.page_margins=PageMargins(left=0.25,right=0.25,top=0.45,bottom=0.45,header=0.2,footer=0.2)
    ws.oddHeader.center.text=f"APSRTC — {display} DEPOT — {period}"
    ws.oddFooter.left.text=f"{display} DEPOT — {period}"
    ws.oddFooter.right.text="Page &P of &N"


def rgb(hexcode):
    return dict(zip(("red","green","blue"),(int(hexcode[i:i+2],16)/255 for i in (0,2,4))))


def google_dashboard_requests(sid,model):
    def region(r,c,rs=1,cs=1):
        return {"sheetId":sid,"startRowIndex":r,"endRowIndex":r+rs,"startColumnIndex":c,"endColumnIndex":c+cs}
    req=[{"updateSheetProperties":{"properties":{"sheetId":sid,"gridProperties":{"rowCount":max(100,model['last_row']),"columnCount":25,"frozenRowCount":0,"frozenColumnCount":0,"hideGridlines":True}},"fields":"gridProperties"}},
         {"unmergeCells":{"range":region(0,0,100,25)}},
         {"updateCells":{"range":region(0,0,100,25),"fields":"userEnteredValue,userEnteredFormat"}}]
    for i,width in enumerate(model["widths"]):
        req.append({"updateDimensionProperties":{"range":{"sheetId":sid,"dimension":"COLUMNS","startIndex":i,"endIndex":i+1},"properties":{"pixelSize":width},"fields":"pixelSize"}})
    req.append({"updateDimensionProperties":{"range":{"sheetId":sid,"dimension":"ROWS","startIndex":0,"endIndex":model["last_row"]},"properties":{"pixelSize":model["height"]},"fields":"pixelSize"}})
    for r,height in [(0,45),(1,34),(12,43)]:
        req.append({"updateDimensionProperties":{"range":{"sheetId":sid,"dimension":"ROWS","startIndex":r,"endIndex":r+1},"properties":{"pixelSize":height},"fields":"pixelSize"}})
    for s in model["cells"]:
        area=region(s['r'],s['c'],s['rs'],s['cs'])
        if s['rs']>1 or s['cs']>1: req.append({"mergeCells":{"range":area,"mergeType":"MERGE_ALL"}})
        fmt={"backgroundColor":rgb(s['fill']),"textFormat":{"fontFamily":"Arial","fontSize":s['size'],"bold":s['bold'],"foregroundColor":rgb(s['color'])},"verticalAlignment":"MIDDLE","horizontalAlignment":s['align'].upper(),"wrapStrategy":"WRAP","numberFormat":{"type":"NUMBER","pattern":s.get("fmt", "General")}}
        req.append({"repeatCell":{"range":area,"cell":{"userEnteredFormat":fmt},"fields":"userEnteredFormat"}})
        v=s['text']; value={} if v is None else {"numberValue":v} if isinstance(v,(float,int)) else {"stringValue":v}
        req.append({"updateCells":{"start":{"sheetId":sid,"rowIndex":s['r'],"columnIndex":s['c']},"rows":[{"values":[{"userEnteredValue":value}]}],"fields":"userEnteredValue"}})
    req.append({"mergeCells":{"range":region(0,14,2,5),"mergeType":"MERGE_ALL"}})
    req.append({"updateCells":{"start":{"sheetId":sid,"rowIndex":0,"columnIndex":14},"rows":[{"values":[{"userEnteredValue":{"formulaValue":f'=IMAGE("{LOGO_URL}",1)'}}]}],"fields":"userEnteredValue"}})
    for s in model["charts"]:
        r=s['source_row']; count=s['points']+1
        source=lambda c:{"sourceRange":{"sources":[region(r,c,count)]}}
        basic={"chartType":"LINE","headerCount":1,"legendPosition":"BOTTOM_LEGEND",
               "domains":[{"domain":source(19)}],"series":[{"series":source(20+j),"targetAxis":"LEFT_AXIS","pointSize":0 if s["targets"][j] else 4,"color":rgb([BLUE,GREEN,ORANGE,NEUTRAL][j%4])} for j in range(s['series'])],
               "axis":[{"position":"LEFT_AXIS","title":s['unit']}],"lineSmoothing":False}
        chart={"spec":{"title":s['title'],"fontName":"Arial","hiddenDimensionStrategy":"SHOW_ALL","basicChart":basic},
               "position":{"overlayPosition":{"anchorCell":{"sheetId":sid,"rowIndex":s['row'],"columnIndex":s['col']},"widthPixels":s['width'],"heightPixels":s['height']}}}
        req.append({"addChart":{"chart":chart}})
    req.append({"updateDimensionProperties":{"range":{"sheetId":sid,"dimension":"COLUMNS","startIndex":19,"endIndex":25},"properties":{"hiddenByUser":True},"fields":"hiddenByUser"}})
    req.append({"updateSheetProperties":{"properties":{"sheetId":sid,"gridProperties":{"frozenRowCount":3}},"fields":"gridProperties.frozenRowCount"}})
    return req

