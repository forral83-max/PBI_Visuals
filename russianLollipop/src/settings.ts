/*
 *  Power BI Visualizations
 *
 *  Copyright (c) Microsoft Corporation
 *  All rights reserved.
 *  MIT License
 *
 *  Permission is hereby granted, free of charge, to any person obtaining a copy
 *  of this software and associated documentation files (the ""Software""), to deal
 *  in the Software without restriction, including without limitation the rights
 *  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 *  copies of the Software, and to permit persons to whom the Software is
 *  furnished to do so, subject to the following conditions:
 *
 *  The above copyright notice and this permission notice shall be included in
 *  all copies or substantial portions of the Software.
 *
 *  THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 *  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 *  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 *  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 *  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 *  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 *  THE SOFTWARE.
 */

"use strict";

import { formattingSettings } from "powerbi-visuals-utils-formattingmodel";

import FormattingSettingsCard = formattingSettings.SimpleCard;
import FormattingSettingsSlice = formattingSettings.Slice;
import FormattingSettingsModel = formattingSettings.Model;

class LollipopCardSettings extends FormattingSettingsCard {
    lineColor = new formattingSettings.ColorPicker({
        name: "lineColor",
        displayName: "Цвет линии",
        value: { value: "#2F6BFF" }
    });

    dotColor = new formattingSettings.ColorPicker({
        name: "dotColor",
        displayName: "Цвет точки",
        value: { value: "#FF5C7A" }
    });

    labelColor = new formattingSettings.ColorPicker({
        name: "labelColor",
        displayName: "Цвет текста",
        value: { value: "#25304A" }
    });

    orientation = new formattingSettings.ItemDropdown({
        name: "orientation",
        displayName: "Ориентация",
        value: { value: "horizontal", displayName: "Горизонтальная" },
        items: [
            { value: "horizontal", displayName: "Горизонтальная" },
            { value: "vertical", displayName: "Вертикальная" }
        ]
    });

    showLabels = new formattingSettings.ToggleSwitch({
        name: "showLabels",
        displayName: "Показывать значения",
        value: true
    });

    lineWidth = new formattingSettings.NumUpDown({
        name: "lineWidth",
        displayName: "Толщина линии",
        value: 3
    });

    dotRadius = new formattingSettings.NumUpDown({
        name: "dotRadius",
        displayName: "Радиус точки",
        value: 7
    });

    fontSize = new formattingSettings.NumUpDown({
        name: "fontSize",
        displayName: "Размер текста",
        value: 12
    });

    name = "lollipop";
    displayName = "Настройки графика";
    slices: Array<FormattingSettingsSlice> = [
        this.orientation,
        this.lineColor,
        this.dotColor,
        this.labelColor,
        this.showLabels,
        this.lineWidth,
        this.dotRadius,
        this.fontSize
    ];
}

/**
* visual settings model class
*
*/
export class VisualFormattingSettingsModel extends FormattingSettingsModel {
    lollipopCard = new LollipopCardSettings();

    cards = [this.lollipopCard];
}
