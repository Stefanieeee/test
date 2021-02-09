/**
 * ViewModel for MCS logger interface
 * @class LoggerViewModel
 * @param {Array} parameters - ViewModel dependencies
 */

function LoggerViewModel (parameters) {
  var self = this
  self.logMessages = ko.observableArray()
  self.length = 20

  self.onDataUpdaterPluginMessage = (id, message) => {
    if (id !== 'ihm_3dprinter_logger') return
    self.logMessages.unshift(message)

    if (self.logMessages().length > self.length) {
      self.logMessages.pop()
    }
  }
}

$(function () {
  OCTOPRINT_VIEWMODELS.push({
    construct: LoggerViewModel,
    elements: ['#mcsLogReader']
  })
})
