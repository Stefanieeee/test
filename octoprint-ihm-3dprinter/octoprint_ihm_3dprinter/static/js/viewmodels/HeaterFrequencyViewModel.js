/**
 * ViewModel for heater frequency interface
 *
 * @class HeaterFrequencyViewModel
 * @param {Array} parameters - ViewModel dependencies
 *
 */

function HeaterFrequencyViewModel (parameters) {
  // General configuration for this viewmodel
  var self = this
  self.octoprint_control = parameters[0]
  setUpValue(self, '10kHz', 'Frequency')
  setUpValuePlot(self, 'Frequency', '.heaterFrequency')
  setUpValuePrecision(self, 0)
  setUpMinMaxValue(self, 245000, 250000)

  /**
   * Handle received data
   *
   * @param {String} id - The sender ID
   * @param {Object} message - The message payload
   *
   */

  self.onDataUpdaterPluginMessage = (id, message) => {
    if (id !== PLUGIN_UID) return
    self.value(message.heater.frequency)
    // For later use
    // self.min(msg.heater.frequency_minimum);
    // self.max(msg.heater.frequency_maximum);
  }

  self.setValue = () => {
    if (!self.newValueValid()) return
    const payload = {
      command: `M405 FREQ${self.newValue()}`
    }
    self.octoprint_control.sendCustomCommand(payload)
    console.info(`Send ${payload.command}`)
  }
}

$(function () {
  OCTOPRINT_VIEWMODELS.push({
    construct: HeaterFrequencyViewModel,
    dependencies: ['controlViewModel'],
  })
})
