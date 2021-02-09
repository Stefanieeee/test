/**
 * ViewModel for PID control interface
 * @class PIDControlViewModel
 * @param {Array} parameters - ViewModel dependencies
 */

function PIDControlViewModel (parameters) {
  var self = this
  self.octoprint_control = parameters[0]
  self.ontime = parameters[1]
  self.offtime = parameters[2]
  self.pwm_power = parameters[3]
  self.power = parameters[4]
  self.pid = parameters[5]
  self.status = parameters[6]
  self.microwave_control = parameters[7]
}

$(function () {
  OCTOPRINT_VIEWMODELS.push({
    construct: PIDControlViewModel,
    dependencies: [
      'controlViewModel',
      'heaterOntimeViewModel',
      'heaterOfftimeViewModel',
      'heaterPWMPowerViewModel',
      'heaterPowerViewModel',
      'temperaturePIDViewModel',
      'heaterStatusViewModel',
      'microwaveControlViewModel'
    ],
    elements:['#pidControlMode']
  })
})
