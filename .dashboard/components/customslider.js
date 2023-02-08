var { Webbit, css, html } = webbit;

class CustomSlider extends Webbit {

  static get dashboardConfig() {
    return {
      displayName: 'Number Slider',
      category: 'General',
      // description: 'A group of checkboxes',
      // documentationLink: 'https://frc-web-components.github.io/components/checkbox-group/',
      slots: [],
      editorTabs: ['properties', 'sources'],
      resizable: { left: true, right: true },
      minSize: { width: 80, height: 10 },
    };
  }

  static get properties() {
    return {
      value: { 
        type: Number, 
        primary: true,
        get() {
          // clamp value
          return Math.max(this.min, Math.min(this._value, this.max));
        }
      },
      min: { 
        type: Number,
        defaultValue: -1,
        get() {
          return Math.min(this._min, this._max);
        }
      },
      max: { 
        type: Number,
        defaultValue: 1,
        get() {
          return Math.max(this._min, this._max);
        }
      },
      blockIncrement: { type: Number, defaultValue: .05 }
    };
  }

  static get styles() {
    return css`
      :host {
        display: inline-block;
        height: 50px;
        width: 300px;
      }
      #slider {
        -webkit-appearance: none;
        width: 100%;
        height: 15px;
        border-radius: 5px;  
        background: var(--lumo-primary-color-50pct);
        outline: none;
        -webkit-transition: .2s;
      }
      #slider::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        width: 25px;
        height: 25px;
        border-radius: 50%; 
        background: var(--lumo-primary-color);
        cursor: pointer;
      }
      #slider::-moz-range-thumb {
        width: 25px;
        height: 25px;
        border-radius: 50%;
        background: var(--lumo-primary-color);
        cursor: pointer;
      }

      .slider-container {
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
      }
      input {
          width: 85%;
          max-width: calc(100% - 60px);
      }
      table-axis {
          width: calc(85% - 14px);
          max-width: calc(100% - 74px);
          display: block;
          fill: var(--lumo-secondary-text-color);
          z-index: -1;
      }
    `;
  }

  onChange(ev) {
    this.value = parseFloat(ev.target.value);
  }

  render() {
    return html`
      <div class="slider-container">
        <input 
          id="slider"
          type="range" 
          min="${this.min}"
          max="${this.max}"
          .value="${this.value.toString()}"
          step="${this.blockIncrement}"
          @change="${this.onChange}"
        />
        <table-axis 
          ticks="5" 
          .range="${[this.min, this.max]}"
        ></table-axis>
      </div>
    `;
  }
}

webbitRegistry.define('frc-custom-slider', CustomSlider);