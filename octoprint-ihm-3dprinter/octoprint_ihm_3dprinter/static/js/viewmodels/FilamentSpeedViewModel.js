/**
 * ViewModel for virtual filament speed sensor interface
 *
 * @class VirtualFilamentSpeedViewModel
 * @param {Array} parameters - ViewModel dependencies
 *
 */

function VirtualFilamentSpeedViewModel (parameters) {
  var self = this
  setUpValue(self, 'mm/s', 'Calc. fil. speed')
  setUpValuePlot(self, 'Calc. fil. speed', '.filamentVirtualSpeedChart')
  setUpValuePrecision(self, 1)

  /**
   * Handle received data
   *
   * @param {String} id - The sender ID
   * @param {Object} message - The message payload
   *
   */

  self.onDataUpdaterPluginMessage = (id, message) => {
    if (id !== PLUGIN_UID) return
    self.value(message.filament_sensor_virtual.speed)
  }
}

/**
 * ViewModel for the filament speed sensor interface
 *
 * @class FilamentSpeedViewModel
 * @param {Array} parameters - ViewModel dependencies
 *
 */

function FilamentSpeedViewModel (parameters) {
  var self = this
  self.octoprint_control = parameters[0]
  setUpValue(self, 'mm/s', 'Meas. fil. speed')
  setUpValuePrecision(self, 1)
  setUpMinMaxValue(self)
  setUpSensor(self)

  self.index = 90
  self.label = 'Filament speed sensor'
  self.chartElementSelectors = [
    {selector: '#sensor-filament-speed-chart', chart: null},
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

  self.setParameters = () => {
    self.setMinimum('M1020', 1)
    self.setMaximum('M1021', 1)
    // self.setOffset('M1022', 1)
    self.setCoefficient('M1023', 1)
  }

  /**
   * Handle received data
   *
   * @param {String} id - The sender ID
   * @param {Object} message - The message payload
   *
   */

  self.onDataUpdaterPluginMessage = (id, message) => {
    if (id !== PLUGIN_UID) return
    self.value(message.filament_sensor.speed)
    self.minimum(message.filament_sensor.minimum)
    self.maximum(message.filament_sensor.maximum)
    self.available(message.filament_sensor.available)
    self.rangeError(message.filament_sensor.out_of_range)
    self.coefficient(message.filament_sensor.coefficient)
    self.offset(message.filament_sensor.offset)
  }
}

$(function () {
  OCTOPRINT_VIEWMODELS.push({
    construct: VirtualFilamentSpeedViewModel,
    dependencies: ['controlViewModel']
  })

  OCTOPRINT_VIEWMODELS.push({
    construct: FilamentSpeedViewModel,
    elements: [
      '#sensor-filament-speed-overview',
      '#sensor-filament-speed-control'
    ],
    dependencies: ['controlViewModel']
  })
})
