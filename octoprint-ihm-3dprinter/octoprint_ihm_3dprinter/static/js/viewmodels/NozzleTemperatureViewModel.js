/**
 * ViewModel for filament pyrometer sensor interface
 *
 * @class FilamentPyrometerTemperatureViewModel
 * @param {Array} parameters - ViewModel dependencies
 *
 */

function FilamentPyrometerTemperatureViewModel (parameters) {
  var self = this
  self.octoprint_control = parameters[0]

  setUpValue(self, '°C', 'Pyrometer')
  setUpValuePrecision(self, 1)
  setUpMinMaxValue(self)
  setUpSensor(self)

  self.setParameters = () => {
    self.setMinimum('M1020', 2)
    self.setMaximum('M1021', 2)
    self.setOffset('M1022', 2)
    self.setCoefficient('M1023', 2)
  }

  self.index = 90
  self.label = 'Pyrometer sensor'
  self.chartElementSelectors = [
    {selector: '#sensor-pyrometer-chart', chart: null},
  ]
  self.chartData = [
    createDataSeries(self.label, 60, 0, self.unit()),
    createDataSeries('Minimum', 60, 'rgba(255,0,0,0.5)', self.unit()),
    createDataSeries('Maximum', 60, 'rgba(255,0,0,0.5)', self.unit())
  ]
  self.chartData[1].hideInLegend = true
  self.chartData[2].hideInLegend = true

  self.updateChart = () => {
    self.index++
    pushToDataSeries(self, 0, self.valueFormatted())
    pushToDataSeries(self, 1, self.minimum())
    pushToDataSeries(self, 2, self.maximum())
    updateChart(self)
  }

  self.onStartupComplete = () => setInterval(() => self.updateChart(), 100)

  /**
   * Handle received data
   *
   * @param {String} id - The sender ID
   * @param {Object} message - The message payload
   *
   */

  self.onDataUpdaterPluginMessage = (id, message) => {
    if (id !== PLUGIN_UID) return
    self.value(message.pyrometer_sensor.value)
    self.minimum(message.pyrometer_sensor.minimum)
    self.maximum(message.pyrometer_sensor.maximum)
    self.available(message.pyrometer_sensor.available)
    self.rangeError(message.pyrometer_sensor.out_of_range)
    self.coefficient(message.pyrometer_sensor.coefficient)
    self.offset(message.pyrometer_sensor.offset)
  }
}

/**
 * ViewModel for filament temperature interface
 *
 * @class FilamentTemperatureViewModel
 * @param {Array} parameters - ViewModel dependencies
 *
 */

function FilamentTemperatureViewModel (parameters) {
  var self = this

  self.octoprint_control = parameters[0]
  self.octoprint_temperatures = parameters[1]

  setUpValue(self, '°C', 'FLIR sensor')
  setUpValuePrecision(self, 1)
  setUpMinMaxValue(self)
  setUpSensor(self)

  self.setParameters = () => {
    self.setMinimum('M1020', 0)
    self.setMaximum('M1021', 0)
    self.setOffset('M1022', 0)
    self.setCoefficient('M1023', 0)
  }

  self.index = 90
  self.label = 'FLIR sensor'
  self.chartElementSelectors = [
    {selector: '#heaterNozzleTemperature', chart: null},
    {selector: '#FLIRSensorChart', chart: null},
  ]
  self.chartData = [
    createDataSeries(self.label, 60, 0, self.unit()),
    createDataSeries('Minimum', 60, 'rgba(255,0,0,0.5)', self.unit()),
    createDataSeries('Maximum', 60, 'rgba(255,0,0,0.5)', self.unit())
  ]
  self.chartData[1].hideInLegend = true
  self.chartData[2].hideInLegend = true

  self.updateChart = () => {
    self.index++
    pushToDataSeries(self, 0, self.valueFormatted())
    pushToDataSeries(self, 1, self.minimum())
    pushToDataSeries(self, 2, self.maximum())
    updateChart(self)
  }

  self.onStartupComplete = () => setInterval(() => self.updateChart(), 100)

  self.target = ko.observable()
  self.newTarget = ko.observable()
  self.target.subscribe(newValue => {
    self.newTarget() === undefined ? self.newTarget(newValue) : null
  })

  self.newBedTarget = ko.observable()
  self.octoprint_temperatures.bedTemp.target.subscribe(newValue => {
    self.newBedTarget() === undefined ? self.newBedTarget(newValue) : null
  })

  // self.available = ko.observable()
  self.getAvailableLabel = ko.computed(() => self.available() ? 'YES' : 'NO', self)

  /**
   * Handle received data
   *
   * @param {String} id - The sender ID
   * @param {Object} message - The message payload
   *
   */

  self.onDataUpdaterPluginMessage = (id, message) => {
    if (id !== PLUGIN_UID) return
    self.value(message.sensor.value)
    self.target(message.temperature.target)
    self.minimum(message.sensor.minimum)
    self.maximum(message.sensor.maximum)
    self.available(message.sensor.available)
    self.rangeError(message.sensor.out_of_range)
    self.coefficient(message.sensor.coefficient)
    self.offset(message.sensor.offset)
  }

  /**
   * Set a preset temperature for the filament heater
   *
   * @param {number} value - The new temperature
   *
   */

  self.setPreset = value => {
    self.newTarget(value)
    self.setTarget(0)
  }

  /**
   * Send the new filament temperature to the host
   *
   * @param {number} change - Modifiy the existing value by this value
   *
   * If change parameter is 0 the temperature from the input field will be used.
   *
   */

  self.setTarget = change => {
    if (change !== 0) {
      self.newTarget(self.target() + change)
    }
    const payload = { command: `M104 S${self.newTarget()}` }
    self.octoprint_control.sendCustomCommand(payload)
    console.info(`Send ${payload.command}`)
    self.target(self.newTarget())
  }

  /**
   * Set a preset temperature for the heated bed
   *
   * @param {number} value - The new temperature
   *
   */

  self.setBedPreset = value => {
    self.newBedTarget(value)
    self.setBedTarget(0)
  }

  /**
   * Send the new bed temperature to the host
   *
   * @param {number} change - Modifiy the existing value by this value
   *
   * If change parameter is 0 the temperature from the input field will be used.
   */

  self.setBedTarget = change => {
    if (change !== 0) {
      self.newBedTarget(self.octoprint_temperatures.bedTemp.target() + change)
    }
    const payload = { command: `M140 S${self.newBedTarget()}` }
    self.octoprint_control.sendCustomCommand(payload)
    console.info(`Send ${payload.command}`)
  }

}

$(function () {
  OCTOPRINT_VIEWMODELS.push({
    construct: FilamentTemperatureViewModel,
    dependencies: ['controlViewModel', 'temperatureViewModel'],
    elements: [
      '#heaterNozzleTemperaturePlot',
      '#heaterNozzleTemperatureControl',
      '#heaterNozzleTemperatureStatus',
      '#bedTemperatureControl',
      '#sensor-filament-temperature-overview',
      '#sensor-filament-temperature-control'
    ]
  })

  OCTOPRINT_VIEWMODELS.push({
    construct: FilamentPyrometerTemperatureViewModel,
    dependencies: ['controlViewModel'],
    elements: [
      '.nozzlePyrometerData',
      '#sensor-pyrometer-overview',
      '#sensor-pyrometer-control'
    ]
  })
})
