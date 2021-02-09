
/**
 * ViewModel for the microwave power sensor interface
 *
 * @class MicrowavePowerSensor
 * @param {Array} parameters - ViewModel dependencies
 *
 */

function MicrowavePowerSensorViewModel (parameters) {
  var self = this
  self.octoprint_control = parameters[0]
  self.forward = ko.observable()
  self.reverse = ko.observable()
  self.peak_envelope = ko.observable()
  self.available = ko.observable()

  self.index = 90
  self.label = 'Filament speed sensor'
  self.chartElementSelectors = [
    {selector: '#sensor-microwave-power-chart', chart: null},
  ]
  self.chartData = [
    createDataSeries('Forward power', 90, 0, 'W'),
    createDataSeries('Reverse power', 90, 1, 'W'),
    createDataSeries('Peak envelope', 90, 2, 'W'),
  ]


  self.updateChart = () => {
    self.index++
    pushToDataSeries(self, 0, self.forward())
    pushToDataSeries(self, 1, self.reverse())
    pushToDataSeries(self, 2, self.peak_envelope())
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
    self.forward(message.microwave_sensor.FWD_AVG)
    self.reverse(message.microwave_sensor.REV_AVG)
    self.peak_envelope(message.microwave_sensor.PEAK_ENV)
    self.available(message.microwave_sensor.available)
  }
}

$(function () {

  OCTOPRINT_VIEWMODELS.push({
    construct: MicrowavePowerSensorViewModel,
    elements: ['#sensor-microwave-power-overview'],
    dependencies: ['controlViewModel']
  })
})
