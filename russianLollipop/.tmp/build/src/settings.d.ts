import { formattingSettings } from "powerbi-visuals-utils-formattingmodel";
import FormattingSettingsCard = formattingSettings.SimpleCard;
import FormattingSettingsSlice = formattingSettings.Slice;
import FormattingSettingsModel = formattingSettings.Model;
declare class LollipopCardSettings extends FormattingSettingsCard {
    lineColor: formattingSettings.ColorPicker;
    dotColor: formattingSettings.ColorPicker;
    labelColor: formattingSettings.ColorPicker;
    orientation: formattingSettings.ItemDropdown;
    showLabels: formattingSettings.ToggleSwitch;
    lineWidth: formattingSettings.NumUpDown;
    dotRadius: formattingSettings.NumUpDown;
    fontSize: formattingSettings.NumUpDown;
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
    cards: LollipopCardSettings[];
}
export {};
