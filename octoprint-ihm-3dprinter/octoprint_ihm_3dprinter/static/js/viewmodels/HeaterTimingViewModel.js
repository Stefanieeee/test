/**
 * ViewModel for the heater ontime interface
 * @class HeaterOntimeViewModel
 * @param {Array} parameters - ViewModel dependencies
 */

function HeaterOntimeViewModel (parameters) {
  var self = this
  self.octoprint_control = parameters[0]
  setUpValue(self, 'ns', 'Ontime')
  setUpMinMaxValue(self, 1000, 1000000)

  self.logarithmicChart = true
  self.index = 90
  self.label = 'Ontime'

  self.chartOptions = {
    yaxis: {
      min: 0,
      mode: 'log',
      transform: function(value) { return value > 0 ? Math.log(value) / Math.LN10 : null },
      inverseTransform: function(value) { return Math.pow(10, value) },
      tickLength: 0,
      show: false
    },
    xaxis: {
      tickFormatter: (value, axis) => '',
    },
    series: {
      lines: {
        lineWidth: 2,
        fill: false
      },
      shadowSize: 0
    },
    grid: {
      borderWidth: 1,
      margin: 0,
      minBorderMargin: 0,
      labelMargin: 0
    },
    legend: {
      position: 'sw',
      backgroundOpacity: 0.8,
      labelFormatter: (label, series) => {
        if (series.hideInLegend === true) {
          return null
        } else {
          return `${label}: ${series.data[series.data.length-1][1]} ${series.unit}`
        }
      }
    }
  }

  self.chartElementSelectors = [
    {selector: '#manual-ontime-chart', chart: null, options: self.chartOptions},
    {selector: '#pid-ontime-chart', chart: null, options: self.chartOptions},
    {selector: '#model-ontime-chart', chart: null, options: self.chartOptions}
  ]

  self.chartData = [
    createDataSeries(self.label, self.index, 'rgba(0,0,0,1)', 'ns'),
    createDataSeries('Minimum', self.index, 'rgba(255,0,0,0.2)', 'ns'),
    createDataSeries('Maximum', self.index, 'rgba(255,0,0,0.2)', 'ns')
  ]

  self.updateChart = () => {

    self.index++
    pushToDataSeries(self, 0, self.value())
    pushToDataSeries(self, 1, self.minimum())
    pushToDataSeries(self, 2, self.maximum())
    updateChart(self)

  }
  self.onStartupComplete = () => setInterval( () => self.updateChart(), 100 )

  /**
   * Handle received data
   * @param {String} id - The sender ID
   * @param {Object} message - The message payload
   */

  self.onDataUpdaterPluginMessage = (id, message) => {
    if (id !== PLUGIN_UID) return
    self.value(message.heater.ontime)
    self.minimum(message.heater.ontime_min)
    self.maximum(message.heater.ontime_max)
  }

  /**
   * Set new ontime limits
   */

  self.setLimits = () => {
    const payload = {
      command: `M401 MIN${self.newMinimum()} MAX${self.newMaximum()}`
    }
    self.octoprint_control.sendCustomCommand(payload)
    console.info(`Send ${payload.command}`)
  }

  /**
   * Set a new ontime
   *
   * @param {number} offset - Apply an offset to the new value
   *
   */

  self.setOntime = () => {
    const payload = {
      command: `M401 VAL${self.newValue()}`
    }
    self.octoprint_control.sendCustomCommand(payload)
    console.info(`Send ${payload.command}`)
    self.value(self.newValue())
  }
}

/**
 * ViewModel for heater offtime interface
 *
 * @class HeaterOfftimeViewModel
 * @param {Array} parameters - ViewModel dependencies
 *
 */

function HeaterOfftimeViewModel (parameters) {
  var self = this
  self.octoprint_control = parameters[0]
  setUpValue(self, 'ns', 'Offtime')
  setUpValuePlot(self, 'Offtime', '.heaterOfftimeChart')
  setUpMinMaxValue(self, 10000, 1000000)

  /**
   * Callback for recieving messages from backend
   *
   * @param {string} id - The id of the sending plugin
   * @param {Object} message - The message object
   *
   */

  self.onDataUpdaterPluginMessage = (id, message) => {
    if (id !== PLUGIN_UID) return
    self.value(message.heater.offtime)
  }

  /**
   * Set a new offtime
   *
   * @param {number} offset - Apply an offset to the new value
   *
   */

  self.setOfftime = offset => {
    if (offset !== 0) {
      self.newValue(self.value() + offset)
    }
    const payload = {
      command: `M402 OFFT${self.newValue()}`
    }
    self.octoprint_control.sendCustomCommand(payload)
    console.info(`Send ${payload.command}`)
    self.value(self.newValue())
  }
}

$(function () {
  OCTOPRINT_VIEWMODELS.push({
    construct: HeaterOntimeViewModel,
    dependencies: ['controlViewModel'],
    elements: ['.heaterOntimeData']
  })
  OCTOPRINT_VIEWMODELS.push({
    construct: HeaterOfftimeViewModel,
    dependencies: ['controlViewModel'],
    elements: ['.heaterOfftimeData']
  })
})
