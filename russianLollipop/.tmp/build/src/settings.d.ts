import { formattingSettings } from "powerbi-visuals-utils-formattingmodel";
import FormattingSettingsCard = formattingSettings.SimpleCard;
import FormattingSettingsSlice = formattingSettings.Slice;
import FormattingSettingsModel = formattingSettings.Model;
declare class LollipopCardSettings extends FormattingSettingsCard {
    stemColor: formattingSettings.ColorPicker;
    planColor: formattingSettings.ColorPicker;
    factColor: formattingSettings.ColorPicker;
    labelColor: formattingSettings.ColorPicker;
    orientation: formattingSettings.ItemDropdown;
    markerShape: formattingSettings.ItemDropdown;
    markerOutlineColor: formattingSettings.ColorPicker;
    markerOutlineWidth: formattingSettings.NumUpDown;
    showLabels: formattingSettings.ToggleSwitch;
    labelPosition: formattingSettings.ItemDropdown;
    lineWidth: formattingSettings.NumUpDown;
    dotRadius: formattingSettings.NumUpDown;
    fontSize: formattingSettings.NumUpDown;
    name: string;
    displayName: string;
    slices: Array<FormattingSettingsSlice>;
}
declare class GridCardSettings extends FormattingSettingsCard {
    showGrid: formattingSettings.ToggleSwitch;
    gridColor: formattingSettings.ColorPicker;
    gridWidth: formattingSettings.NumUpDown;
    name: string;
    displayName: string;
    slices: Array<FormattingSettingsSlice>;
}
declare class AxesCardSettings extends FormattingSettingsCard {
    showAxis: formattingSettings.ToggleSwitch;
    axisColor: formattingSettings.ColorPicker;
    axisTextColor: formattingSettings.ColorPicker;
    axisFontSize: formattingSettings.NumUpDown;
    name: string;
    displayName: string;
    slices: Array<FormattingSettingsSlice>;
}
/**
* visual settings model class
*
*/
export declare class VisualFormattingSettingsModel extends FormattingSettingsModel {
    lollipopCard: LollipopCardSettings;
    gridCard: GridCardSettings;
    axesCard: AxesCardSettings;
    cards: (LollipopCardSettings | GridCardSettings | AxesCardSettings)[];
}
export {};
