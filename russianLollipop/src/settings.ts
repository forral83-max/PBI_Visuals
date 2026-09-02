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
    stemColor = new formattingSettings.ColorPicker({
        name: "stemColor",
        displayName: "Цвет линии",
        value: { value: "#2F6BFF" }
    });

    planColor = new formattingSettings.ColorPicker({
        name: "planColor",
        displayName: "Цвет плана",
        value: { value: "#2F6BFF" }
    });

    factColor = new formattingSettings.ColorPicker({
        name: "factColor",
        displayName: "Цвет факта",
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

    markerShape = new formattingSettings.ItemDropdown({
        name: "markerShape",
        displayName: "Форма маркера",
        value: { value: "circle", displayName: "Круг" },
        items: [
            { value: "circle", displayName: "Круг" },
            { value: "square", displayName: "Квадрат" },
            { value: "diamond", displayName: "Ромб" }
        ]
    });

    markerOutlineColor = new formattingSettings.ColorPicker({
        name: "markerOutlineColor",
        displayName: "Обводка маркера",
        value: { value: "#FFFFFF" }
    });

    markerOutlineWidth = new formattingSettings.NumUpDown({
        name: "markerOutlineWidth",
        displayName: "Толщина обводки",
        value: 2
    });

    showLabels = new formattingSettings.ToggleSwitch({
        name: "showLabels",
        displayName: "Показывать значения",
        value: true
    });

    labelPosition = new formattingSettings.ItemDropdown({
        name: "labelPosition",
        displayName: "Положение подписи",
        value: { value: "side", displayName: "Сбоку" },
        items: [
            { value: "side", displayName: "Сбоку" },
            { value: "top", displayName: "Сверху" },
            { value: "bottom", displayName: "Снизу" }
        ]
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
        this.stemColor,
        this.planColor,
        this.factColor,
        this.labelColor,
        this.showLabels,
        this.labelPosition,
        this.lineWidth,
        this.fontSize,
        this.markerShape,
        this.dotRadius,
        this.markerOutlineColor,
        this.markerOutlineWidth
    ];
}

class GridCardSettings extends FormattingSettingsCard {
    showGrid = new formattingSettings.ToggleSwitch({
        name: "showGrid",
        displayName: "Показывать сетку",
        value: true
    });

    gridColor = new formattingSettings.ColorPicker({
        name: "gridColor",
        displayName: "Цвет сетки",
        value: { value: "#D8DEEA" }
    });

    gridWidth = new formattingSettings.NumUpDown({
        name: "gridWidth",
        displayName: "Толщина сетки",
        value: 1
    });

    name = "grid";
    displayName = "Сетка";
    slices: Array<FormattingSettingsSlice> = [this.showGrid, this.gridColor, this.gridWidth];
}

class AxesCardSettings extends FormattingSettingsCard {
    showAxis = new formattingSettings.ToggleSwitch({
        name: "showAxis",
        displayName: "Показывать оси",
        value: true
    });

    axisColor = new formattingSettings.ColorPicker({
        name: "axisColor",
        displayName: "Цвет осей",
        value: { value: "#8792A8" }
    });

    axisTextColor = new formattingSettings.ColorPicker({
        name: "axisTextColor",
        displayName: "Цвет подписей осей",
        value: { value: "#5E6A80" }
    });

    axisFontSize = new formattingSettings.NumUpDown({
        name: "axisFontSize",
        displayName: "Размер подписей осей",
        value: 11
    });

    name = "axes";
    displayName = "Оси";
    slices: Array<FormattingSettingsSlice> = [this.showAxis, this.axisColor, this.axisTextColor, this.axisFontSize];
}

/**
* visual settings model class
*
*/
export class VisualFormattingSettingsModel extends FormattingSettingsModel {
    lollipopCard = new LollipopCardSettings();
    gridCard = new GridCardSettings();
    axesCard = new AxesCardSettings();

    cards = [this.lollipopCard, this.gridCard, this.axesCard];
}
