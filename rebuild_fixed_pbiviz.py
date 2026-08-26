#!/usr/bin/env python3
import json
import re
import shutil
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parent
src_zip = root / 'ChicletSlicer_WrapText_ShowValue_v2.pbiviz'
out_zip = root / 'ChicletSlicer_WrapText_ShowValue_v2_fixed.pbiviz'
tmp_dir = root / '.tmp_pbiviz_fix'

if tmp_dir.exists():
    shutil.rmtree(tmp_dir)
tmp_dir.mkdir(parents=True, exist_ok=True)

with zipfile.ZipFile(src_zip, 'r') as zf:
    zf.extractall(tmp_dir)

pkg_path = tmp_dir / 'package.json'
pkg = json.loads(pkg_path.read_text(encoding='utf-8'))
pkg['version'] = '2.2.3.3-custom'
pkg['visual']['version'] = '2.2.3.3-custom'
pkg['visual']['displayName'] = 'Chiclet Slicer (Wrap + Value) 2.2.3.3-custom'
pkg['visual']['name'] = 'chicletSlicerWrapValue'
pkg['visual']['guid'] = 'ChicletSlicerWrapValue1756000000001'
pkg['visual']['visualClassName'] = 'ChicletSlicer'
pkg_path.write_text(json.dumps(pkg, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

resource_path = next(tmp_dir.glob('resources/*.json'))
resource = json.loads(resource_path.read_text(encoding='utf-8'))
js = resource['content']['js']
css = resource['content']['css']

# Add new formatting options: label text alignment and value spacing.
js = js.replace(
    'const d=[{displayName:"Visual_ValuePosition_Below",value:"Below"},{displayName:"Visual_ValuePosition_Right",value:"Right"}];',
    'const d=[{displayName:"Visual_ValuePosition_Below",value:"Below"},{displayName:"Visual_ValuePosition_Right",value:"Right"}];const x=[{displayName:"Visual_Text_Align_Left",value:"Left"},{displayName:"Visual_Text_Align_Center",value:"Center"},{displayName:"Visual_Text_Align_Right",value:"Right"}];'
)

js = js.replace(
    'this.valuePosition=new r.z.PA({name:"valuePosition",displayNameKey:"Visual_Value_Position",items:d,value:d[0]}),this.height=new r.z.iB({name:"height",displayNameKey:"Visual_Height",value:y.DefaultValue,options:{minValue:{type:0,value:y.MinValue}}}),',
    'this.valuePosition=new r.z.PA({name:"valuePosition",displayNameKey:"Visual_Value_Position",items:d,value:d[0]}),this.labelTextAlign=new r.z.PA({name:"labelTextAlign",displayNameKey:"Visual_Text_Align",items:x,value:x[1]}),this.valueSpacing=new r.z.iB({name:"valueSpacing",displayNameKey:"Visual_Value_Spacing",value:6,options:{minValue:{type:0,value:0},maxValue:{type:1,value:50}}}),this.height=new r.z.iB({name:"height",displayNameKey:"Visual_Height",value:y.DefaultValue,options:{minValue:{type:0,value:y.MinValue}}}),'
)

js = js.replace(
    'this.slices=[this.textSize,this.tailoring,this.wordWrap,this.showValue,this.valueFontColor,this.valueFontSize,this.valuePosition,this.height,this.width,this.background,this.transparency,this.selectedColor,this.hoverColor,this.unselectedColor,this.disabledColor,this.outlineColor,this.outlineWeight,this.fontColor,this.padding,this.borderStyle]',
    'this.slices=[this.textSize,this.tailoring,this.wordWrap,this.showValue,this.valueFontColor,this.valueFontSize,this.valuePosition,this.labelTextAlign,this.valueSpacing,this.height,this.width,this.background,this.transparency,this.selectedColor,this.hoverColor,this.unselectedColor,this.disabledColor,this.outlineColor,this.outlineWeight,this.fontColor,this.padding,this.borderStyle]'
)

js = js.replace(
    'const r=e.selectAll(v.LabelTextSelector.selectorName),i=e.selectAll(v.ValueTextSelector.selectorName),n=e.selectAll(v.SlicerTextWrapperSelector.selectorName),l=v.getChicletTextProperties(a.slicerTextCardSettings.textSize.value),d=t.formatString,c=t.valueFormatString,p=a.slicerTextCardSettings.wordWrap.value,f=a.slicerTextCardSettings.showValue.value&&!!t.hasValueField,m="Right"===a.slicerTextCardSettings.valuePosition.value.value,y=this.getSlicerBodyViewport(this.currentViewport,a.headerCardSettings,t.selfFilterEnabled);if(n.classed("valuePositionRight",m&&f),r.classed("wordWrap",p).text(e=>{l.text=u.G2.format(e.category,d),a.slicerTextCardSettings.width.value=Math.floor(y.width/(this.tableView.computedColumns||v.MinColumns));const t=a.slicerTextCardSettings.width.value-v.СhicletTotalInnerRightLeftPaddings-v.СellTotalInnerBorders-a.slicerTextCardSettings.outlineWeight.value;return a.slicerTextCardSettings.tailoring.value?u.Tf.getTailoredTextOrDefault(l,t):l.text}),i.classed("hidden",!f).classed("valuePositionRight",m).style("color",a.slicerTextCardSettings.valueFontColor.value.value).style("font-size",o.fromPoint(a.slicerTextCardSettings.valueFontSize.value)).text(e=>f&&null!==e.value&&void 0!==e.value&&isFinite(e.value)?u.G2.format(e.value,c):""),e.style("padding",o.toString(a.slicerTextCardSettings.padding.value)),',
    'const r=e.selectAll(v.LabelTextSelector.selectorName),i=e.selectAll(v.ValueTextSelector.selectorName),n=e.selectAll(v.SlicerTextWrapperSelector.selectorName),l=v.getChicletTextProperties(a.slicerTextCardSettings.textSize.value),d=t.formatString,c=t.valueFormatString,p=a.slicerTextCardSettings.wordWrap.value,f=a.slicerTextCardSettings.showValue.value&&!!t.hasValueField,m="Right"===a.slicerTextCardSettings.valuePosition.value.value,y=this.getSlicerBodyViewport(this.currentViewport,a.headerCardSettings,t.selfFilterEnabled);const valueRight=m&&f;const textAlign=(a.slicerTextCardSettings.labelTextAlign&&a.slicerTextCardSettings.labelTextAlign.value&&a.slicerTextCardSettings.labelTextAlign.value.value)||"Center";const valueSpacing=(a.slicerTextCardSettings.valueSpacing&&void 0!==a.slicerTextCardSettings.valueSpacing.value?a.slicerTextCardSettings.valueSpacing.value:6);if(n.classed("valuePositionRight",valueRight).style("display","flex").style("flex-direction",valueRight?"row":"column").style("align-items",valueRight?"baseline":"stretch").style("justify-content",valueRight?"center":"center").style("text-align",textAlign).style("column-gap",valueRight?`${valueSpacing}px`:null).style("row-gap",valueRight?`${valueSpacing}px`:null),r.classed("wordWrap",p).style("display",valueRight?"inline-block":"block").style("text-align",textAlign).style("margin-right",valueRight?`${valueSpacing}px`:null).text(e=>{l.text=u.G2.format(e.category,d),a.slicerTextCardSettings.width.value=Math.floor(y.width/(this.tableView.computedColumns||v.MinColumns));const t=a.slicerTextCardSettings.width.value-v.СhicletTotalInnerRightLeftPaddings-v.СellTotalInnerBorders-a.slicerTextCardSettings.outlineWeight.value;return a.slicerTextCardSettings.tailoring.value?u.Tf.getTailoredTextOrDefault(l,t):l.text}),i.classed("hidden",!f).classed("valuePositionRight",m).style("display",valueRight?"inline-block":"block").style("margin-left",valueRight?`${valueSpacing}px`:null).style("vertical-align",valueRight?"baseline":"middle").style("text-align",valueRight?textAlign:"center").style("color",a.slicerTextCardSettings.valueFontColor.value.value).style("font-size",o.fromPoint(a.slicerTextCardSettings.valueFontSize.value)).text(e=>f&&null!==e.value&&void 0!==e.value&&isFinite(e.value)?u.G2.format(e.value,c):""),e.style("padding",o.toString(a.slicerTextCardSettings.padding.value)),'
)

css = css.replace(
    '.chicletSlicer .slicer-text-wrapper.valuePositionRight {\n  flex-direction: row;\n  flex-wrap: wrap;\n  align-items: baseline;\n  justify-content: center;\n  column-gap: 6px;\n}\n.chicletSlicer .slicerValueText.valuePositionRight {\n  display: inline;\n  width: auto;\n}\n',
    '.chicletSlicer .slicer-text-wrapper.valuePositionRight {\n  display: flex;\n  flex-direction: row;\n  flex-wrap: wrap;\n  align-items: baseline;\n  justify-content: center;\n  column-gap: 6px;\n}\n.chicletSlicer .slicerText.valuePositionRight {\n  display: inline-block;\n  text-align: inherit;\n}\n.chicletSlicer .slicerValueText.valuePositionRight {\n  display: inline-block;\n  width: auto;\n  margin-left: 0;\n}\n'
)

# Force correct text alignment behaviour when label alignment is chosen.
css = css.replace(
    '.chicletSlicer .slicerBody li.slicerItemContainer .slicer-text-wrapper {\n  box-sizing: border-box;\n  text-align: center;\n',
    '.chicletSlicer .slicerBody li.slicerItemContainer .slicer-text-wrapper {\n  box-sizing: border-box;\n  text-align: center;\n'
)

# Ensure english string resources contain new labels.
string_resources = resource['stringResources']['en-US']
for key, value in {
    'Visual_Text_Align': 'Text alignment',
    'Visual_Text_Align_Left': 'Left',
    'Visual_Text_Align_Center': 'Center',
    'Visual_Text_Align_Right': 'Right',
    'Visual_Value_Spacing': 'Value spacing',
}.items():
    string_resources[key] = value

resource['content']['js'] = js
resource['content']['css'] = css
resource_path.write_text(json.dumps(resource, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

with zipfile.ZipFile(out_zip, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
    for file in sorted(tmp_dir.rglob('*')):
        if file.is_file():
            zf.write(file, file.relative_to(tmp_dir))

print(f'Created {out_zip}')
