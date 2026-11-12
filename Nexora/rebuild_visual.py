from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "nexoraKPI74A92BB1DAE480BBC09C4B425BA7001.5.9.1.0.pbiviz"
OUTPUT = ROOT / "nexoraKPI_5.9.3.0_patched.pbiviz"
ORIGINAL_RESOURCE = "resources/nexoraKPI74A92BB1DAE480BBC09C4B425BA7001.pbiviz.json"
PATCHED_GUID = "nexoraKPI8C2D6F1A4B9E4370A5D1C8F3B6E2A904"
VERSION = "5.9.3.0"
DISPLAY_NAME = "Nexora KPI Enhanced 5.9.3"
RESOURCE = f"resources/{PATCHED_GUID}.pbiviz.json"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)


def add_role(capabilities: dict) -> None:
    roles = capabilities["dataRoles"]
    note_roles = [
        ("note", "Back note value", "Optional text measure shown on the flip-card back"),
        ("note2", "Back note value 2", "Optional second text measure shown on the flip-card back"),
        ("note3", "Back note value 3", "Optional third text measure shown on the flip-card back"),
    ]
    for name, display_name, description in note_roles:
        if not any(role["name"] == name for role in roles):
            roles.append(
                {
                    "displayName": display_name,
                    "name": name,
                    "kind": "Measure",
                    "description": description,
                }
            )

    condition = capabilities["dataViewMappings"][0]["conditions"][0]
    for name, _, _ in note_roles:
        condition.setdefault(name, {})["max"] = 1
    values = capabilities["dataViewMappings"][0]["categorical"]["values"]["select"]
    for name, _, _ in note_roles:
        if not any(item.get("bind", {}).get("to") == name for item in values):
            values.append({"bind": {"to": name}})


def add_property(group: dict, name: str, descriptor: dict) -> None:
    group.setdefault("properties", {})[name] = descriptor


def update_capabilities(p: dict) -> None:
    c = p["capabilities"]
    add_role(c)

    objects = c["objects"]
    enum_type = lambda items: {"enumeration": [{"value": value, "displayName": label} for value, label in items]}
    fill_type = {"fill": {"solid": {"color": True}}}

    add_property(objects["presetOptions"], "gaugeDeltaPosition", {"type": enum_type([
        ("below", "Below gauge"),
        ("above", "Above gauge"),
        ("right", "Right of gauge"),
    ])})
    add_property(objects["delta"], "fontSize", {"type": {"numeric": True}})

    add_property(objects["target"], "labelText", {"type": {"text": True}})
    add_property(objects["target"], "labelPosition", {"type": enum_type([
        ("top", "Above bar"),
        ("bottom", "Below bar"),
        ("inline", "Inline"),
    ])})
    add_property(objects["target"], "labelFontSize", {"type": {"numeric": True}})
    add_property(objects["target"], "labelColor", {"type": fill_type})

    add_property(objects["flip"], "backTitleColor", {"type": fill_type})
    add_property(objects["flip"], "backLabelFontSize", {"type": {"numeric": True}})
    add_property(objects["flip"], "segmentPercentLabel", {"type": {"text": True}})
    add_property(objects["flip"], "percentChangeLabel", {"type": {"text": True}})

    p["visual"]["guid"] = PATCHED_GUID
    p["visual"]["version"] = VERSION
    p["visual"]["displayName"] = DISPLAY_NAME
    p["visual"].pop("supportUrl", None)
    p["visual"].pop("gitHubUrl", None)
    p["visual"]["description"] = (
        "Nexora KPI — configurable KPI card with Russian and English labels, "
        "seven styles, target labels, sparklines, flip-card details and selection effects."
    )


def patch_formatting_classes(js: str) -> str:
    js = replace_once(
        js,
        'gaugeTrackColor=new i.z.sk({name:"gaugeTrackColor",displayName:"Track color",value:{value:"#f0f0ec"}});accentBarWidth=',
        'gaugeTrackColor=new i.z.sk({name:"gaugeTrackColor",displayName:"Track color",value:{value:"#f0f0ec"}});gaugeDeltaPosition=new i.z.PA({name:"gaugeDeltaPosition",displayName:"Gauge Delta position",items:[{value:"below",displayName:"Below gauge"},{value:"above",displayName:"Above gauge"},{value:"right",displayName:"Right of gauge"}],value:{value:"below",displayName:"Below gauge"}});accentBarWidth=',
        "gauge delta formatting setting",
    )
    js = replace_once(
        js,
        'this.gaugeShowPercent,this.gaugeThickness,this.gaugeTrackColor,this.accentBarWidth',
        'this.gaugeShowPercent,this.gaugeThickness,this.gaugeTrackColor,this.gaugeDeltaPosition,this.accentBarWidth',
        "gauge delta slice",
    )
    js = replace_once(
        js,
        'gauge:["gaugeShowPercent","gaugeThickness","gaugeTrackColor"]',
        'gauge:["gaugeShowPercent","gaugeThickness","gaugeTrackColor","gaugeDeltaPosition"]',
        "gauge delta format visibility",
    )
    js = replace_once(
        js,
        't.gaugeShowPercent,t.gaugeThickness,t.gaugeTrackColor,t.accentBarWidth',
        't.gaugeShowPercent,t.gaugeThickness,t.gaugeTrackColor,t.gaugeDeltaPosition,t.accentBarWidth',
        "gauge delta format slice list",
    )
    js = replace_once(
        js,
        'invertColors=new i.z.jF({name:"invertColors",displayName:"Invert (lower is better)",value:!1});name="delta";displayName="Delta";slices=[this.show,this.asPercent,this.positiveColor,this.negativeColor,this.invertColors]}class c',
        'invertColors=new i.z.jF({name:"invertColors",displayName:"Invert (lower is better)",value:!1});fontSize=new i.z.iB({name:"fontSize",displayName:"Font size",value:12});name="delta";displayName="Delta";slices=[this.show,this.asPercent,this.positiveColor,this.negativeColor,this.invertColors,this.fontSize]}class c',
        "delta font size setting",
    )

    js = replace_once(
        js,
        'showLabel=new i.z.jF({name:"showLabel",displayName:"Show target value text",value:!0});achievedColor=',
        'showLabel=new i.z.jF({name:"showLabel",displayName:"Show target value text",value:!0});labelText=new i.z.ks({name:"labelText",displayName:"Target label",placeholder:"e.g. Target",value:"Target"});labelPosition=new i.z.PA({name:"labelPosition",displayName:"Label position",items:[{value:"top",displayName:"Above bar"},{value:"bottom",displayName:"Below bar"},{value:"inline",displayName:"Inline"}],value:{value:"top",displayName:"Above bar"}});labelFontSize=new i.z.iB({name:"labelFontSize",displayName:"Label font size",value:10});labelColor=new i.z.sk({name:"labelColor",displayName:"Label color",value:{value:"#8A8A95"}});achievedColor=',
        "target label formatting settings",
    )
    js = replace_once(
        js,
        'this.style,this.showLabel,this.achievedColor',
        'this.style,this.showLabel,this.labelText,this.labelPosition,this.labelFontSize,this.labelColor,this.achievedColor',
        "target label slices",
    )

    js = replace_once(
        js,
        'backTitle=new i.z.ks({name:"backTitle",displayName:"Back face — Title",placeholder:"e.g. Details",value:"تفاصيل المؤشّر"});backContent=',
        'backTitle=new i.z.ks({name:"backTitle",displayName:"Back face — Title",placeholder:"e.g. Details",value:"Details"});backTitleColor=new i.z.sk({name:"backTitleColor",displayName:"Back title color",value:{value:"#A07E3F"}});backContent=',
        "flip title color",
    )
    js = replace_once(
        js,
        'showSegPercent=new i.z.jF({name:"showSegPercent",displayName:"Show category %",value:!0});statValueLabel=',
        'showSegPercent=new i.z.jF({name:"showSegPercent",displayName:"Show category %",value:!0});segmentPercentLabel=new i.z.ks({name:"segmentPercentLabel",displayName:"Category percentage label",placeholder:"e.g. Category %",value:"Category %"});percentChangeLabel=new i.z.ks({name:"percentChangeLabel",displayName:"Percent change label",placeholder:"e.g. Change %",value:"Change %"});statValueLabel=',
        "flip percentage labels",
    )
    js = replace_once(
        js,
        'backFontSize=new i.z.iB({name:"backFontSize",displayName:"Font size",value:12});backValueFontSize=',
        'backFontSize=new i.z.iB({name:"backFontSize",displayName:"Font size",value:12});backLabelFontSize=new i.z.iB({name:"backLabelFontSize",displayName:"Back label font size",value:12});backValueFontSize=',
        "flip label font size",
    )
    js = replace_once(
        js,
        'this.showDelta,this.showPercentChange,this.showSegPercent,this.statValueLabel',
        'this.showDelta,this.showPercentChange,this.showSegPercent,this.segmentPercentLabel,this.percentChangeLabel,this.statValueLabel',
        "flip percentage label slices",
    )
    js = replace_once(
        js,
        'this.backTextColor,this.backAccentColor,this.backBorderColor,this.backFontSize,this.backValueFontSize',
        'this.backTextColor,this.backAccentColor,this.backBorderColor,this.backTitleColor,this.backFontSize,this.backLabelFontSize,this.backValueFontSize',
        "flip color and font slices",
    )
    return js


def patch_data_extraction(js: str) -> str:
    js = replace_once(
        js,
        'let a=0,i=null,l=!1,s="",n="",o="",r=null,d=null,c=null,u=null,p="";',
        'let a=0,i=null,l=!1,s="",n="",o="",r=null,d=null,c=null,u=null,p="",L=null,q=null,Q=null,Z=null;',
        "extract data state",
    )
    js = replace_once(
        js,
        'i.target&&!u&&(u=a,p=a.source.displayName||"Target")}',
        'i.target&&!u?(u=a,p=a.source.displayName||"Target"):i.label&&!L?(L=a):i.note&&!q?q=a:i.note2&&!Q?Q=a:i.note3&&!Z&&(Z=a)}',
        "label and note roles",
    )
    js = replace_once(
        js,
        'null===N&&(N=m(e),0===N&&0===e.length&&(N=null))}return null!==h',
        'null===N&&(N=m(e),0===N&&0===e.length&&(N=null))}const E=e=>{const t=null!=e.highlights?e.highlights:e.values||[];for(const e of t)if(null!=e)return String(e);return""};let R=q?E(q):"",F=Q?E(Q):"",I=Z?E(Z):"";if(L&&L.values&&L.values.length>0){const e=null!=L.highlights?L.highlights:L.values||[];for(const t of e)if(null!=t){s=String(t);break}}return null!==h',
        "text measure extraction",
    )
    js = replace_once(
        js,
        'target:N,targetName:p}',
        'target:N,targetName:p,noteText:R,noteText2:F,noteText3:I}',
        "note data returned",
    )
    return js


def patch_rendering(js: str) -> str:
    js = replace_once(
        js,
        'if(i.style.background=t.styleCard.backgroundColor.value.value,',
        'if(i.style.setProperty("background-color",t.styleCard.backgroundColor.value.value,"important"),i.style.setProperty("background-image","none","important"),',
        "background color application",
    )
    js = replace_once(
        js,
        'i.style.background="linear-gradient("+e.angle.value+"deg, "+e.startColor.value.value+", "+e.endColor.value.value+")",i.classList.add("kpi-gradient-bg")',
        'i.style.setProperty("background-image","linear-gradient("+e.angle.value+"deg, "+e.startColor.value.value+", "+e.endColor.value.value+")","important"),i.style.setProperty("background-color","transparent","important"),i.classList.add("kpi-gradient-bg")',
        "card gradient application",
    )
    js = replace_once(
        js,
        'i.style.cursor="pointer",i.addEventListener("click",a=>{',
        'i.style.cursor="pointer",i.setAttribute("role","button"),i.setAttribute("tabindex","0"),i.setAttribute("aria-label",e.label||e.measureName||"KPI card"),i.addEventListener("click",a=>{',
        "card keyboard semantics",
    )
    js = replace_once(
        js,
        '})});const o=e=>{const t=this.target.getBoundingClientRect();return[e.clientX-t.left,e.clientY-t.top]};switch(i.addEventListener("mouseover",t=>{',
        '})}),i.addEventListener("keydown",a=>{"Enter"!==a.key&&" "!==a.key||(!e.selectionId||(a.preventDefault(),this.selectionManager.select(e.selectionId,a.ctrlKey||a.metaKey).then(e=>{this.applySelectionState(e.length>0)})))});const o=e=>{const t=this.target.getBoundingClientRect();return[e.clientX-t.left,e.clientY-t.top]};switch(i.addEventListener("mouseover",t=>{',
        "card keyboard selection",
    )
    js = replace_once(
        js,
        'default:this.renderDefault(i,e)}if(e.breakdown.length>0',
        'default:this.renderDefault(i,e)}if("default"!==a&&t.iconCard.show.value){const e=this.makeIcon();if(e){const a=i.querySelector(".kpi-body")||i,l=t.iconCard.position.value.value;if("inline"===l){const t=a.querySelector(".kpi-value");if(t&&t.parentNode){const i=this.el("div","kpi-icon-inline-row");t.parentNode.insertBefore(i,t),i.appendChild(e),i.appendChild(t)}else a.insertBefore(e,a.firstChild)}else a.insertBefore(e,a.firstChild)}}if(e.breakdown.length>0',
        "icons in every preset",
    )
    front_tooltip = 'dataItems:this.buildTooltipItems(e),identities:[]'
    if js.count(front_tooltip) != 2:
        raise RuntimeError(f"front tooltip identity: expected 2 matches, found {js.count(front_tooltip)}")
    js = js.replace(front_tooltip, 'dataItems:this.buildTooltipItems(e),identities:e.selectionId?[e.selectionId]:[]')
    back_tooltip = 'dataItems:this.buildTooltipItems(t),identities:[]'
    if js.count(back_tooltip) != 2:
        raise RuntimeError(f"back tooltip identity: expected 2 matches, found {js.count(back_tooltip)}")
    js = js.replace(back_tooltip, 'dataItems:this.buildTooltipItems(t),identities:t.selectionId?[t.selectionId]:[]')
    js = replace_once(
        js,
        'const a=e.value-e.comparison,i=a/Math.abs(e.comparison)*100;t.push({displayName:"Change",value:(a>=0?"▲ ":"▼ ")+Math.abs(i).toFixed(1)+"%"})',
        'const a=e.value-e.comparison,i=0!==e.comparison?a/Math.abs(e.comparison)*100:null;t.push({displayName:"Change",value:null===i?"N/A":(a>=0?"▲ ":"▼ ")+Math.abs(i).toFixed(1)+"%"})',
        "tooltip zero guard",
    )
    js = replace_once(
        js,
        'return a.textContent=n,a.style.color=s,a.style.background=this.hexAlpha(s,.12),a}',
        'return a.textContent=n,a.style.color=s,a.style.fontSize=Math.max(8,t.fontSize&&t.fontSize.value||12)+"px",a.style.background=this.hexAlpha(s,.12),a}',
        "delta font size application",
    )
    js = replace_once(
        js,
        't.style.background=`linear-gradient(${e}deg, ${i} 0%, ${l} 33%, ${s} 66%, ${n} 100%)`',
        't.style.setProperty("background",`linear-gradient(${e}deg, ${i} 0%, ${l} 33%, ${s} 66%, ${n} 100%)`,"important")',
        "selection gradient",
    )
    js = replace_once(
        js,
        'else t.style.background=a.fillColor.value.value;const e=a.textColorOnSelect',
        'else t.style.setProperty("background",a.fillColor.value.value,"important");const e=a.textColorOnSelect',
        "selection solid",
    )
    js = replace_once(
        js,
        'else t.style.background=t._origBg||"",t.style.removeProperty("--nx-select-text")',
        'else t.style.removeProperty("background"),t._origBg&&t.style.setProperty("background",t._origBg),t.style.removeProperty("--nx-select-text")',
        "selection restore",
    )
    js = replace_once(
        js,
        'const r=this.formattingSettings.selectionCard;r&&(l&&(r.gradColor1.value={value:l}),s&&(r.gradColor2.value={value:s}),n&&(r.gradColor3.value={value:n}),o&&(r.gradColor4.value={value:o}),l&&(r.rippleColor.value={value:l}));const d=this.formattingSettings.flipCard;',
        'const d=this.formattingSettings.flipCard;',
        "preserve user selection gradient colors",
    )
    js = replace_once(
        js,
        'if(t.gradientCard.show.value&&!t.styleCard.transparentBackground.value){const e=t.gradientCard;i.style.setProperty("background-image","linear-gradient("+e.angle.value+"deg, "+e.startColor.value.value+", "+e.endColor.value.value+")","important"),i.style.setProperty("background-color","transparent","important"),i.classList.add("kpi-gradient-bg")}this.applyConditionalColor(i,e);',
        'this.applyConditionalColor(i,e);if(t.gradientCard.show.value){const e=t.gradientCard;i.style.setProperty("background-image","linear-gradient("+e.angle.value+"deg, "+e.startColor.value.value+", "+e.endColor.value.value+")","important"),i.style.setProperty("background-color","transparent","important"),i.classList.add("kpi-gradient-bg")}else i.style.setProperty("background-image","none","important");',
        "gradient applied after conditional color",
    )
    js = replace_once(
        js,
        'destroy(){this.resizeObserver&&(this.resizeObserver.disconnect(),this.resizeObserver=null),null!==this.autoFitRaf&&(window.cancelAnimationFrame(this.autoFitRaf),this.autoFitRaf=null)}',
        'destroy(){this.resizeObserver&&(this.resizeObserver.disconnect(),this.resizeObserver=null),null!==this.autoFitRaf&&(window.cancelAnimationFrame(this.autoFitRaf),this.autoFitRaf=null),null!==this.valueAnimationId&&(window.cancelAnimationFrame(this.valueAnimationId),this.valueAnimationId=null)}',
        "destroy animation cleanup",
    )
    return js


def replace_gauge(js: str) -> str:
    start = js.index("renderGauge(e,t){")
    end = js.index("renderCompact(e,t){", start)
    old = js[start:end]
    new = '''renderGauge(e,t){const a=this.formattingSettings.presetOptionsCard,i=this.el("div","kpi-gauge-body"),l=this.el("div","kpi-gauge-content"),s=a.gaugeDeltaPosition&&a.gaugeDeltaPosition.value?a.gaugeDeltaPosition.value.value:"below",n=this.shouldShowDelta(t)?this.makeDelta(t):null;i.classList.add("kpi-gauge-delta-"+s),"above"===s&&n&&l.appendChild(n),l.appendChild(this.makeLabel(t)),l.appendChild(this.makeValue(t)),"below"===s&&n&&l.appendChild(n);const o=t.hasComparison&&t.comparison?t.comparison:t.value,r=o>0?Math.min(t.value/o*100,100):0,d=this.formattingSettings.styleCard.accentColor.value.value,c=Math.max(2,a.gaugeThickness.value),u=a.gaugeTrackColor.value.value,p=2*Math.PI*24,h=p-r/100*p,m=this.svgEl("svg");m.setAttribute("viewBox","0 0 64 64"),m.setAttribute("preserveAspectRatio","xMidYMid meet"),m.classList.add("kpi-gauge-svg");const v=this.svgEl("circle");v.setAttribute("cx",String(32)),v.setAttribute("cy",String(32)),v.setAttribute("r",String(24)),v.setAttribute("fill","none"),v.setAttribute("stroke",u),v.setAttribute("stroke-width",String(c)),m.appendChild(v);const g=this.svgEl("circle");if(g.setAttribute("cx",String(32)),g.setAttribute("cy",String(32)),g.setAttribute("r",String(24)),g.setAttribute("fill","none"),g.setAttribute("stroke",d),g.setAttribute("stroke-width",String(c)),g.setAttribute("stroke-dasharray",String(p)),g.setAttribute("stroke-dashoffset",String(h)),g.setAttribute("stroke-linecap","round"),g.setAttribute("transform","rotate(-90 32 32)"),m.appendChild(g),a.gaugeShowPercent.value){const e=this.svgEl("text");e.setAttribute("x",String(32)),e.setAttribute("y",String(36)),e.setAttribute("text-anchor","middle"),e.setAttribute("font-size","13"),e.setAttribute("font-weight","700"),e.setAttribute("fill","currentColor"),e.textContent=r.toFixed(0)+"%",m.appendChild(e)}i.appendChild(l),i.appendChild(m),"right"===s&&n&&i.appendChild(n),e.appendChild(i)}
'''
    return js[:start] + new + js[end:]


def replace_target(js: str) -> str:
    start = js.index("appendTargetIndicator(e,t){")
    end = js.index("formatValue(e){", start)
    new = '''appendTargetIndicator(e,t){const a=this.formattingSettings.targetCard;if(!a||!a.show.value||null===t.target||0===t.target)return;const i=t.value/t.target*100,l=a.style.value.value,s=a.behindAt.value;let n;n=i>=a.onTrackAt.value?a.achievedColor.value.value:i<s?a.behindColor.value.value:a.inProgressColor.value.value;const o=this.el("div","kpi-target"),r=(a.labelText&&a.labelText.value||t.targetName||"Target").trim()||"Target",d=a.labelPosition&&a.labelPosition.value?a.labelPosition.value.value:"top",c=this.el("span","kpi-target-label",r);c.style.fontSize=Math.max(8,a.labelFontSize&&a.labelFontSize.value||10)+"px",c.style.color=a.labelColor&&a.labelColor.value?a.labelColor.value.value:"#8A8A95";"top"===d&&a.showLabel.value&&o.appendChild(c);if(a.showLabel.value||"percent"===l||"both"===l){const e=this.el("div","kpi-target-row");"inline"===d&&a.showLabel.value&&e.appendChild(c),"percent"!==l&&"both"!==l||(()=>{const e=this.el("span","kpi-target-pct",i.toFixed(0)+"%");e.style.color=n,e.style.fontWeight="700",e.appendChild(document.createTextNode("")),e&&e;return e})(),"percent"!==l&&"both"!==l||e.appendChild((()=>{const e=this.el("span","kpi-target-pct",i.toFixed(0)+"%");return e.style.color=n,e.style.fontWeight="700",e})()),a.showLabel.value&&e.appendChild(this.el("span","kpi-target-goal","/ "+this.formatValue(t.target))),o.appendChild(e)}if("bar"===l||"both"===l){const e=this.el("div","kpi-target-track");e.style.background=a.trackColor.value.value;const t=this.el("div","kpi-target-fill"),l=Math.max(0,Math.min(100,i));t.style.width=l+"%",t.style.background=n,i>100&&e.classList.add("kpi-target-over"),e.appendChild(t),o.appendChild(e)}"bottom"===d&&a.showLabel.value&&o.appendChild(c),e.appendChild(o)}
'''
    return js[:start] + new + js[end:]


def patch_flip(js: str) -> str:
    js = replace_once(
        js,
        'd.style.fontSize=h+"px";const m=(a.flipCard.backTitle.value||"").trim();if(m){const e=this.el("div","kpi-back-title",m);e.style.color=a.flipCard.backAccentColor.value.value',
        'd.style.fontSize=h+"px";const m=(a.flipCard.backTitle.value||"").trim();if(m){const e=this.el("div","kpi-back-title",m);e.style.color=a.flipCard.backTitleColor&&a.flipCard.backTitleColor.value?a.flipCard.backTitleColor.value.value:a.flipCard.backAccentColor.value.value,e.style.fontSize=(a.flipCard.backFontSize.value||13)+"px"',
        "flip title style",
    )
    js = replace_once(
        js,
        'const n=this.el("div","kpi-stat-row"),o=this.el("span","kpi-stat-label",e),r=this.el("span","kpi-stat-value",t);s&&s.accent',
        'const n=this.el("div","kpi-stat-row"),o=this.el("span","kpi-stat-label",e),r=this.el("span","kpi-stat-value",t);o.style.fontSize=(this.formattingSettings.flipCard.backLabelFontSize&&this.formattingSettings.flipCard.backLabelFontSize.value||12)+"px",s&&s.accent',
        "flip label size",
    )
    js = replace_once(
        js,
        's("نسبة التغيّر",(t>=0?"▲ ":"▼ ")+Math.abs(t).toFixed(1)+"%",{color:t>=0?"#15803D":"#B42318",bold:!0})',
        's(this.formattingSettings.flipCard.percentChangeLabel&&this.formattingSettings.flipCard.percentChangeLabel.value||"Change %",(t>=0?"▲ ":"▼ ")+Math.abs(t).toFixed(1)+"%",{color:t>=0?"#15803D":"#B42318",bold:!0})',
        "flip percent change label",
    )
    js = replace_once(
        js,
        't.showSegPercent.value&&i>0&&(r+="  ·  "+(s.value/i*100).toFixed(0)+"%")',
        't.showSegPercent.value&&i>0&&(r+="  ·  "+(t.segmentPercentLabel&&t.segmentPercentLabel.value||"Category %")+": "+(s.value/i*100).toFixed(0)+"%")',
        "flip category percent label",
    )
    js = replace_once(
        js,
        'const k=(a.flipCard.backText.value||"").trim();if(k){const e=this.el("div","kpi-back-text",k)',
        'const k=(a.flipCard.backText.value||[t.noteText,t.noteText2,t.noteText3].filter(Boolean).join("\\n")).trim();if(k){const e=this.el("div","kpi-back-text",k)',
        "multiple text measures back note",
    )
    return js


def remove_external_links(js: str) -> str:
    js, count = re.subn(
        r'const v=this\.el\("div","nx-landing-cta".*?l\.appendChild\(v\);',
        "",
        js,
        count=1,
    )
    if count != 1:
        raise RuntimeError(f"landing CTA removal: expected 1 match, found {count}")

    js, count = re.subn(
        r'const C=this\.el\("div","nx-landing-links"\).*?l\.appendChild\(C\),t\.appendChild\(l\);',
        "t.appendChild(l);",
        js,
        count=1,
    )
    if count != 1:
        raise RuntimeError(f"landing links removal: expected 1 match, found {count}")

    start = js.find("makeLandingLink(e,t,a){")
    if start < 0:
        raise RuntimeError("landing link method not found")
    end = js.find("makeLabel(e){", start)
    if end < 0:
        raise RuntimeError("makeLabel after landing link method not found")
    js = js[:start] + 'makeLandingLink(e,t,a){return this.el("div","nx-landing-link",t)}' + js[end:]

    for url in (
        "https://nexoraanalysis.com",
        "https://www.linkedin.com",
        "mailto:contact@nexoraanalysis.com",
    ):
        if url in js:
            raise RuntimeError(f"external link remains in JavaScript: {url}")
    return js


def patch_locale_and_text(js: str) -> str:
    js = js.replace('toLocaleString("en-US",', 'toLocaleString(this.host&&this.host.locale||void 0,')
    replacements = {
        "تفاصيل المؤشّر": "Детали показателя",
        "القيمة الحالية": "Текущее значение",
        "القيمة المرجعية": "Сравнительное значение",
        "الفرق": "Разница",
        "SAR (ر.س)": "SAR",
        "AED (د.إ)": "AED",
        "KWD (د.ك)": "KWD",
        "QAR (ر.ق)": "QAR",
        "BHD (د.ب)": "BHD",
        "OMR (ر.ع)": "OMR",
        "EGP (ج.م)": "EGP",
        "(فارغ)": "(Пусто)",
        "اقلب البطاقة · Flip card": "Перевернуть карточку",
        "نسبة التغيّر": "Изменение, %",
        "landingLang=\"ar\"": "landingLang=\"ru\"",
        '"ar"===this.landingLang': '"ru"===this.landingLang',
        'this.landingLang=e?"en":"ar"': 'this.landingLang=e?"en":"ru"',
        "العربية": "Русский",
        "التبديل إلى العربية": "Переключить на русский",
        "التبديل إلى Русский": "Переключить на русский",
        "نيكسورا": "NEXORA",
        "مؤشّر الأداء": "Показатель эффективности",
        "بطاقة مؤشّر أداء أنيقة تعرض القيمة والتغيّر والاتجاه بنظرة واحدة، مع دعم كامل للعربية ورمز الريال الجديد.": "Карточка показателя с отображением значения, изменения и тренда.",
        "رمز الريال الجديد": "Новый символ рияла",
        "دعم عربي": "Поддержка русского языка",
        "مؤشّر اتجاه": "Индикатор тренда",
        "اعرف المزيد": "Подробнее",
        "اسحب حقلاً للبدء (رقم أو نص أو تاريخ) · خصّص من لوحة الإعدادات": "Перетащите поле для начала работы (число, текст или дата) · настройте визуал в панели форматирования",
        "الموقع": "Сайт",
        "تواصل": "Контакты",
        "معاينة الشكل": "Предпросмотр",
        "مثال توضيحي — الشكل الفعلي يعتمد على بياناتك": "Демонстрация — фактический вид зависит от данных",
        "الأداء": "Показатель",
        "أعلى · Max: ${this.formatValue(u)}": "Максимум · Max: ${this.formatValue(u)}",
        "أدنى · Min: ${this.formatValue(c)}": "Минимум · Min: ${this.formatValue(c)}",
        "الفرق · Change: ${v>=0?\"+\":\"\"}${g.toFixed(1)}%": "Изменение · Change: ${v>=0?\"+\":\"\"}${g.toFixed(1)}%",
        "ر.س": "SAR",
        "د.إ": "AED",
        "د.ك": "KWD",
        "ر.ق": "QAR",
        "د.ب": "BHD",
        "ر.ع": "OMR",
        "ج.م": "EGP",
    }
    for old, new in replacements.items():
        js = js.replace(old, new)
    return js


def append_css(css: str) -> str:
    return css + """
/* Nexora KPI 5.9.3.0 fixes */
.kpi-icon-inline-row { display: flex; align-items: center; gap: 10px; min-width: 0; }
.kpi-icon-inline-row .kpi-value { flex: 1; min-width: 0; }
.kpi-gauge-content { min-width: 0; display: flex; flex-direction: column; justify-content: center; }
.kpi-gauge-delta-above .kpi-gauge-content .kpi-delta { order: -1; margin-top: 0; margin-bottom: 8px; }
.kpi-gauge-delta-right .kpi-delta { align-self: center; margin-top: 0; }
.kpi-target { display: flex; flex-direction: column; gap: 4px; }
.kpi-target-label { display: block; font-weight: 600; line-height: 1.2; }
.kpi-target-row { display: flex; align-items: center; gap: 5px; min-width: 0; }
.kpi-target-goal { color: inherit; opacity: .75; }
.kpi-target-track { width: 100%; }
.kpi-target-label + .kpi-target-row { margin-top: 1px; }
.kpi-back-text { white-space: pre-wrap; }
"""


def russian_resources() -> dict:
    return {
        "Visual_Role_Value": "Значение",
        "Visual_Role_Comparison": "Сравнительное значение",
        "Visual_Role_Label": "Переопределение подписи",
        "Visual_Role_Breakdown": "Разбивка",
        "Visual_Role_Trend": "Тренд",
        "Visual_Role_Target": "Цель",
        "Card_Style": "Стиль",
        "Prop_BackgroundColor": "Фон",
        "Prop_TransparentBg": "Прозрачный фон",
        "Prop_BorderRadius": "Радиус границ",
        "Prop_Preset": "Предустановленный стиль",
        "Card_Label": "Подпись",
        "Card_Value": "Значение",
        "Prop_FontSize": "Размер шрифта",
        "Prop_FontBold": "Жирный",
        "Prop_Prefix": "Префикс",
        "Prop_Suffix": "Суффикс",
        "Prop_DisplayUnits": "Единицы отображения",
        "Prop_Decimals": "Десятичные знаки",
        "Prop_FontColor": "Цвет текста",
        "Card_NumberFormat": "Формат чисел",
        "Prop_ValueType": "Тип значения",
        "Prop_ValueTypeNumber": "Число",
        "Prop_ValueTypePercent": "Процент",
        "Prop_ValueTypeCurrency": "Валюта",
        "Prop_PercentScale": "Масштаб процента",
        "Prop_CurrencyCode": "Валюта",
        "Prop_CurrencyPosition": "Положение валюты",
        "Card_Delta": "Разница",
        "Card_Sparkline": "Мини-график",
        "Card_Target": "Цель",
        "Common_Show": "Показывать",
    }


def main() -> None:
    with zipfile.ZipFile(SOURCE) as archive:
        package = json.loads(archive.read("package.json"))
        visual = json.loads(archive.read(ORIGINAL_RESOURCE))

    package["version"] = VERSION
    package["visual"]["version"] = VERSION
    package["visual"]["guid"] = PATCHED_GUID
    package["visual"]["displayName"] = DISPLAY_NAME
    package["visual"].pop("supportUrl", None)
    package["visual"].pop("gitHubUrl", None)
    package["resources"][0]["file"] = RESOURCE
    update_capabilities(visual)

    js = visual["content"]["js"]
    js = patch_formatting_classes(js)
    js = patch_data_extraction(js)
    js = patch_rendering(js)
    js = replace_gauge(js)
    js = replace_target(js)
    js = patch_flip(js)
    js = patch_locale_and_text(js)
    js = remove_external_links(js)
    js = js.replace("nexoraKPI74A92BB1DAE480BBC09C4B425BA7001", PATCHED_GUID)
    visual["content"]["js"] = js
    visual["content"]["css"] = append_css(visual["content"]["css"])
    visual["stringResources"] = {"en-US": visual["stringResources"]["en-US"], "ru-RU": russian_resources()}

    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("package.json", json.dumps(package, ensure_ascii=False, indent=2) + "\n")
        archive.writestr("resources/", b"")
        archive.writestr(RESOURCE, json.dumps(visual, ensure_ascii=False, separators=(",", ":")))

    print(f"built {OUTPUT.name}")
    print(f"js={len(js)} css={len(visual['content']['css'])} roles={len(visual['capabilities']['dataRoles'])}")


if __name__ == "__main__":
    main()
