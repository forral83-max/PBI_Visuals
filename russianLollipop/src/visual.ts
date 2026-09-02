/*
*  Power BI Visual CLI
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

import powerbi from "powerbi-visuals-api";
import { FormattingSettingsService } from "powerbi-visuals-utils-formattingmodel";
import "./../style/visual.less";

import VisualConstructorOptions = powerbi.extensibility.visual.VisualConstructorOptions;
import VisualUpdateOptions = powerbi.extensibility.visual.VisualUpdateOptions;
import IVisual = powerbi.extensibility.visual.IVisual;
import ISelectionId = powerbi.visuals.ISelectionId;
import ISelectionManager = powerbi.extensibility.ISelectionManager;
import DataView = powerbi.DataView;

import { VisualFormattingSettingsModel } from "./settings";

type LabelPlacement = {
    x: number;
    y: number;
    text: string;
    width: number;
    height: number;
    anchor: string;
};

export class Visual implements IVisual {
    private target: HTMLElement;
    private svg: SVGSVGElement;
    private formattingSettings: VisualFormattingSettingsModel;
    private formattingSettingsService: FormattingSettingsService;
    private selectionManager: ISelectionManager;
    private host: powerbi.extensibility.visual.IVisualHost;

    constructor(options: VisualConstructorOptions) {
        this.formattingSettingsService = new FormattingSettingsService();
        this.target = options.element;
        this.host = options.host;
        this.selectionManager = options.host.createSelectionManager();
        this.svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        this.svg.classList.add("lollipop-visual");
        this.target.appendChild(this.svg);
    }

    public update(options: VisualUpdateOptions) {
        const dataView: DataView | undefined = options.dataViews && options.dataViews[0];
        this.formattingSettings = this.formattingSettingsService.populateFormattingSettingsModel(
            VisualFormattingSettingsModel,
            dataView
        );
        this.render(dataView, options.viewport.width, options.viewport.height);
    }

    private render(dataView: DataView | undefined, width: number, height: number): void {
        while (this.svg.firstChild) {
            this.svg.removeChild(this.svg.firstChild);
        }
        this.svg.setAttribute("width", String(width));
        this.svg.setAttribute("height", String(height));
        this.svg.setAttribute("viewBox", `0 0 ${width} ${height}`);

        const categories = dataView?.categorical?.categories?.[0];
        const valueColumns = dataView?.categorical?.values;
        if (!categories || !valueColumns?.length || width < 20 || height < 20) {
            return;
        }

        const points = categories.values.map((category, index) => ({
            category: String(category ?? ""),
            values: valueColumns.slice(0, 2).map((column) => Number(column.values[index])),
            selectionId: this.createSelectionId(categories, index)
        })).filter((point) => point.values.some((value) => Number.isFinite(value)));
        if (!points.length) {
            return;
        }

        const settings = this.formattingSettings.lollipopCard;
        const gridSettings = this.formattingSettings.gridCard;
        const axisSettings = this.formattingSettings.axesCard;
        const horizontal = settings.orientation.value.value === "horizontal";
        const labelFontSize = this.clamp(Number(settings.fontSize.value), 8, 24);
        const lineWidth = this.clamp(Number(settings.lineWidth.value), 1, 12);
        const dotRadius = this.clamp(Number(settings.dotRadius.value), 3, 24);
        const outlineWidth = this.clamp(Number(settings.markerOutlineWidth.value), 0, 8);
        const axisFontSize = this.clamp(Number(axisSettings.axisFontSize.value), 8, 20);
        const margin = horizontal
            ? { top: 12, right: 64, bottom: 12, left: Math.min(width * 0.42, 180) }
            : { top: 28, right: 16, bottom: Math.min(height * 0.34, 100), left: 42 };
        const chartWidth = Math.max(1, width - margin.left - margin.right);
        const chartHeight = Math.max(1, height - margin.top - margin.bottom);
        const allValues = points.flatMap((point) => point.values).filter((value) => Number.isFinite(value));
        const minimum = Math.min(0, ...allValues);
        const maximum = Math.max(0, ...allValues);
        const range = maximum - minimum || 1;
        const valuePosition = (value: number): number => (value - minimum) / range;
        const baseline = horizontal
            ? margin.left + chartWidth * valuePosition(0)
            : margin.top + chartHeight - chartHeight * valuePosition(0);

        if (gridSettings.showGrid.value) {
            this.drawGrid(horizontal, margin, chartWidth, chartHeight, minimum, maximum,
                gridSettings.gridColor.value.value, this.clamp(Number(gridSettings.gridWidth.value), 1, 5),
                axisSettings.axisTextColor.value.value, axisFontSize);
        }
        if (axisSettings.showAxis.value) {
            this.appendLine(horizontal ? baseline : margin.left, horizontal ? margin.top : baseline,
                horizontal ? baseline : margin.left + chartWidth, horizontal ? margin.top + chartHeight : baseline,
                axisSettings.axisColor.value.value, 1);
        }

        const placedLabels: LabelPlacement[] = [];
        points.forEach((point, index) => {
            const slot = (index + 0.5) / points.length;
            const axisPosition = horizontal
                ? margin.top + chartHeight * slot
                : margin.left + chartWidth * slot;
            const validValues = point.values.filter((value) => Number.isFinite(value));
            const stemValue = Math.max(0, ...validValues);
            const stemEndpoint = horizontal
                ? { x: margin.left + chartWidth * valuePosition(stemValue), y: axisPosition }
                : { x: axisPosition, y: margin.top + chartHeight - chartHeight * valuePosition(stemValue) };
            this.svg.appendChild(this.createSvgLine(
                horizontal ? baseline : axisPosition,
                horizontal ? axisPosition : baseline,
                stemEndpoint.x,
                stemEndpoint.y,
                settings.stemColor.value.value,
                lineWidth
            ));
            point.values.forEach((value, valueIndex) => {
                if (!Number.isFinite(value)) {
                    return;
                }
                const endpoint = horizontal
                    ? { x: margin.left + chartWidth * valuePosition(value), y: axisPosition }
                    : { x: axisPosition, y: margin.top + chartHeight - chartHeight * valuePosition(value) };
                const color = valueIndex === 0 ? settings.planColor.value.value : settings.factColor.value.value;
                const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
                group.style.cursor = "pointer";
                const marker = this.createMarker(endpoint.x, endpoint.y, dotRadius, color,
                    settings.markerOutlineColor.value.value, outlineWidth, String(settings.markerShape.value.value));
                group.appendChild(marker);
                if (settings.showLabels.value) {
                    const labelPosition = String(settings.labelPosition.value.value);
                    const labelCoordinates = this.getLabelCoordinates(
                        endpoint.x,
                        endpoint.y,
                        value,
                        dotRadius,
                        labelFontSize,
                        labelPosition,
                        horizontal
                    );
                    const labelText = this.formatValue(value);
                    const resolvedLabel = this.resolveLabelCollision(
                        labelCoordinates,
                        labelText,
                        labelFontSize,
                        String(settings.labelPosition.value.value),
                        horizontal,
                        placedLabels
                    );
                    placedLabels.push(resolvedLabel);
                    group.appendChild(this.createText(
                        resolvedLabel.x,
                        resolvedLabel.y,
                        labelText,
                        settings.labelColor.value.value,
                        labelFontSize,
                        resolvedLabel.anchor,
                        "value-label"
                    ));
                }
                group.addEventListener("click", (event) => {
                    this.selectionManager.select(point.selectionId, (event as MouseEvent).ctrlKey);
                });
                group.addEventListener("mouseenter", () => marker.setAttribute("opacity", "0.75"));
                group.addEventListener("mouseleave", () => marker.setAttribute("opacity", "1"));
                this.svg.appendChild(group);
            });
            this.svg.appendChild(this.createText(
                horizontal ? margin.left - 8 : axisPosition,
                horizontal ? axisPosition + labelFontSize * 0.35 : height - margin.bottom + labelFontSize + 6,
                point.category,
                settings.labelColor.value.value,
                labelFontSize,
                horizontal ? "end" : "middle",
                "category-label"
            ));
        });
    }

    private createSelectionId(categories: powerbi.DataViewCategoryColumn, index: number): ISelectionId {
        return this.host.createSelectionIdBuilder().withCategory(categories, index).createSelectionId();
    }

    private appendLine(x1: number, y1: number, x2: number, y2: number, color: string, width: number): void {
        this.svg.appendChild(this.createSvgLine(x1, y1, x2, y2, color, width));
    }

    private drawGrid(horizontal: boolean, margin: { top: number; right: number; bottom: number; left: number },
        chartWidth: number, chartHeight: number, minimum: number, maximum: number, color: string,
        width: number, textColor: string, fontSize: number): void {
        const tickCount = 5;
        const range = maximum - minimum || 1;
        for (let tickIndex = 0; tickIndex <= tickCount; tickIndex++) {
            const value = minimum + range * tickIndex / tickCount;
            const ratio = tickIndex / tickCount;
            if (horizontal) {
                const x = margin.left + chartWidth * ratio;
                this.appendLine(x, margin.top, x, margin.top + chartHeight, color, width);
                this.svg.appendChild(this.createText(x, margin.top + chartHeight + fontSize + 4,
                    this.formatValue(value), textColor, fontSize, "middle", "axis-label"));
            } else {
                const y = margin.top + chartHeight - chartHeight * ratio;
                this.appendLine(margin.left, y, margin.left + chartWidth, y, color, width);
                this.svg.appendChild(this.createText(margin.left - 8, y + fontSize * 0.35,
                    this.formatValue(value), textColor, fontSize, "end", "axis-label"));
            }
        }
    }

    private createMarker(x: number, y: number, radius: number, color: string, outlineColor: string,
        outlineWidth: number, shape: string): SVGElement {
        const marker = document.createElementNS("http://www.w3.org/2000/svg", shape === "circle" ? "circle" : "rect");
        if (shape === "circle") {
            marker.setAttribute("cx", String(x));
            marker.setAttribute("cy", String(y));
            marker.setAttribute("r", String(radius));
        } else {
            const size = shape === "diamond" ? radius * 1.5 : radius * 2;
            marker.setAttribute("x", String(x - size / 2));
            marker.setAttribute("y", String(y - size / 2));
            marker.setAttribute("width", String(size));
            marker.setAttribute("height", String(size));
            if (shape === "diamond") {
                marker.setAttribute("transform", `rotate(45 ${x} ${y})`);
            }
        }
        marker.setAttribute("fill", color);
        marker.setAttribute("stroke", outlineColor);
        marker.setAttribute("stroke-width", String(outlineWidth));
        return marker;
    }

    private getLabelCoordinates(x: number, y: number, value: number, radius: number,
        fontSize: number, position: string, horizontal: boolean): { x: number; y: number; anchor: string } {
        if (position === "top") {
            return { x, y: y - radius - 6, anchor: "middle" };
        }
        if (position === "bottom") {
            return { x, y: y + radius + fontSize + 2, anchor: "middle" };
        }
        if (horizontal) {
            return {
                x: x + (value >= 0 ? radius + 5 : -radius - 5),
                y: y + fontSize * 0.35,
                anchor: value >= 0 ? "start" : "end"
            };
        }
        return { x: x + radius + 5, y: y + fontSize * 0.35, anchor: "start" };
    }

    private resolveLabelCollision(base: { x: number; y: number; anchor: string }, text: string,
        fontSize: number, position: string, horizontal: boolean, placedLabels: LabelPlacement[]): LabelPlacement {
        const width = Math.max(fontSize * 1.5, text.length * fontSize * 0.58);
        const height = fontSize * 1.25;
        const step = height + 3;
        const offsets = [0, -step, step, -step * 2, step * 2, -step * 3, step * 3];
        const movesAlongScale = horizontal !== (position === "side");
        for (const offset of offsets) {
            const candidate: LabelPlacement = {
                x: base.x + (movesAlongScale ? offset : 0),
                y: base.y + (movesAlongScale ? 0 : offset),
                text,
                width,
                height,
                anchor: base.anchor
            };
            if (!placedLabels.some((label) => this.labelsOverlap(candidate, label))) {
                return candidate;
            }
        }
        return {
            x: base.x + (movesAlongScale ? step : 0),
            y: base.y + (movesAlongScale ? 0 : step),
            text,
            width,
            height,
            anchor: base.anchor
        };
    }

    private labelsOverlap(first: LabelPlacement, second: LabelPlacement): boolean {
        const firstLeft = first.anchor === "end" ? first.x - first.width : first.anchor === "middle" ? first.x - first.width / 2 : first.x;
        const secondLeft = second.anchor === "end" ? second.x - second.width : second.anchor === "middle" ? second.x - second.width / 2 : second.x;
        const horizontalOverlap = firstLeft < secondLeft + second.width && firstLeft + first.width > secondLeft;
        const verticalOverlap = Math.abs(first.y - second.y) < Math.max(first.height, second.height);
        return horizontalOverlap && verticalOverlap;
    }

    private createSvgLine(x1: number, y1: number, x2: number, y2: number, color: string, width: number): SVGLineElement {
        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", String(x1));
        line.setAttribute("y1", String(y1));
        line.setAttribute("x2", String(x2));
        line.setAttribute("y2", String(y2));
        line.setAttribute("stroke", color);
        line.setAttribute("stroke-width", String(width));
        line.setAttribute("stroke-linecap", "round");
        return line;
    }

    private createText(x: number, y: number, text: string, color: string, size: number, anchor: string, className: string): SVGTextElement {
        const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
        label.setAttribute("x", String(x));
        label.setAttribute("y", String(y));
        label.setAttribute("fill", color);
        label.setAttribute("font-size", String(size));
        label.setAttribute("text-anchor", anchor);
        label.setAttribute("class", className);
        label.textContent = text;
        return label;
    }

    private formatValue(value: number): string {
        return new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 2 }).format(value);
    }

    private clamp(value: number, minimum: number, maximum: number): number {
        return Number.isFinite(value) ? Math.min(maximum, Math.max(minimum, value)) : minimum;
    }

    /**
     * Returns properties pane formatting model content hierarchies, properties and latest formatting values, Then populate properties pane.
     * This method is called once every time we open properties pane or when the user edit any format property. 
     */
    public getFormattingModel(): powerbi.visuals.FormattingModel {
        return this.formattingSettingsService.buildFormattingModel(this.formattingSettings);
    }
}