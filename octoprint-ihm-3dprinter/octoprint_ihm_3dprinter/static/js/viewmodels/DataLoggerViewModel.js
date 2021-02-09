/**
 * ViewModel for datalogger interface
 *
 * @class CombinedPowerSensorViewModel
 * @param {Array} parameters - ViewModel dependencies
 *
 */

function DataLoggerViewModel (parameters) {
  var self = this
  self.octoprint_control = parameters[0]
  self.active = ko.observable()
  self.records = ko.observable()
  self.files = ko.observable()
  // self.start_date = ko.observable()
  // self.stop_date = ko.observable()
  self.stop_count = ko.observable()
  self.stop_duration = ko.observable()
  self.data_dir = ko.observable()
  self.activeLabel = ko.computed(() => self.active() ? 'ACTIVE' : 'INACTIVE')

  /**
   * Handle received data
   *
   * @param {String} id - The sender ID
   * @param {Object} message - The message payload
   *
   */

  self.onDataUpdaterPluginMessage = (id, message) => {
    if (id !== `${PLUGIN_UID}_datalogger`) return
    self.active(message.active)
    self.records(message.index)
    self.stop_count(message.stop_count)
    self.data_dir(message.data_dir)
    self.files(message.files)
  }

  /**
   * Send the command to start the datalogger
   */

  self.start = () => {
    const payload = { command: 'M1010' }
    self.octoprint_control.sendCustomCommand(payload)
    console.info(`Send ${payload.command}`)
  }

  /**
   * Send the command to stop the datalogger
   */

  self.stop = () => {
    const payload = { command: 'M1011' }
    self.octoprint_control.sendCustomCommand(payload)
    console.info(`Send ${payload.command}`)
  }

  /**
   * Send the command to dump the datalogger in an CSV file
   */

  self.dump = () => {
    const payload = { command: 'M1012' }
    self.octoprint_control.sendCustomCommand(payload)
    console.info(`Send ${payload.command}`)
  }
}

$(function () {
  OCTOPRINT_VIEWMODELS.push({
    construct: DataLoggerViewModel,
    dependencies: ['controlViewModel'],
    elements: ['#dataloggerControl']
  })
})
