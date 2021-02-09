/**
 * ViewModel for combined temperature chart
 *
 * @class CombinedTemperatureViewModel
 *
 */

function CombinedTemperatureViewModel (parameters) {
  var self = this
  self.thermal_camera = parameters[0]
  self.pyrometer_sensor = parameters[1]
  self.octoprint_temperatures = parameters[2]

  // Chart configuration starts here
  self.index = 180
  self.chartElementSelectors = [
    { selector: '.combinedTemperatureChart', chart: null }
  ]
  self.chartData = [
    createDataSeries(self.thermal_camera.label, self.index, 'rgba(0,0,255)', self.thermal_camera.unit()),
    createDataSeries(self.pyrometer_sensor.label, self.index, 'rgb(0,255,0)', self.pyrometer_sensor.unit()),
    createDataSeries('Bed', self.index, 'rgba(255,0,0,1)', '°C'),
    createDataSeries('Bed target', self.index, 'rgba(255,0,0,0.2)', '°C'),
    createDataSeries('FLIR target', self.index, 'rgba(0,0,255,0.2)', '°C')
  ]

  self.chartData[3].hideInLegend = true
  self.chartData[4].hideInLegend = true

  /**
   * Update the data series and redraw the chart
   */

  self.updateChart = () => {
    self.index++
    pushToDataSeries(self, 0, self.thermal_camera.valueFormatted())
    pushToDataSeries(self, 1, self.pyrometer_sensor.valueFormatted())
    pushToDataSeries(self, 2, self.octoprint_temperatures.bedTemp.actual())
    pushToDataSeries(self, 3, self.octoprint_temperatures.bedTemp.target())
    pushToDataSeries(self, 4, self.thermal_camera.target())
    updateChart(self)
  }

  /**
   * Start the interval timer once everything is loaded
   */

  self.onStartupComplete = () => setInterval(() => self.updateChart(), 100)
}

/**
 * ViewModel for combined timings chart
 *
 * @class CombinedTimingViewModel
 *
 */

function CombinedTimingViewModel (parameters) {
  var self = this
  self.ontime = parameters[0]
  self.offtime = parameters[1]

  // Chart configuration starts here
  self.index = 90
  self.chartElementSelectors = [
    { selector: '.combinedTimingChart', chart: null }
  ]
  self.chartData = [
    createDataSeries(self.ontime.label, self.index, 0, self.ontime.unit()),
    createDataSeries(self.offtime.label, self.index, 0, self.offtime.unit())
  ]

  /**
   * Update the data series and redraw the chart
   */

  self.updateChart = () => {
    self.index++
    pushToDataSeries(self, 0, self.ontime.value())
    pushToDataSeries(self, 1, self.offtime.value())
    updateChart(self)
  }

  /**
   * Start the interval timer once everything is loaded
   */

  self.onStartupComplete = () => setInterval(() => self.updateChart(), 100)
}

/**
 * ViewModel for combined power sensor chart
 *
 * @class CombinedPowerSensorViewModel
 *
 */

function CombinedPowerSensorViewModel (parameters) {
  var self = this
  self.reflected = parameters[0]
  self.forward = parameters[1]

  // Chart configuration starts here
  self.index = 90
  self.chartElementSelectors = [
    { selector: '.combinedPowerSensorChart', chart: null }
  ]
  self.chartData = [
    createDataSeries(self.reflected.label, self.index, 0, self.reflected.unit()),
    createDataSeries(self.forward.label, self.index, 1, self.forward.unit())
  ]

  /**
   * Update the data series and redraw the chart
   */

  self.updateChart = () => {
    self.index++
    pushToDataSeries(self, 0, self.reflected.value())
    pushToDataSeries(self, 1, self.forward.value())
    updateChart(self)
  }

  /**
   * Start the interval timer once everything is loaded
   */

  self.onStartupComplete = () => setInterval(() => self.updateChart(), 100)
}

/**
 * ViewModel for combined filament speed sensor chart
 *
 * @class CombinedFilamendSpeedViewModel
 *
 */

function CombinedFilamendSpeedViewModel (parameters) {
  var self = this
  self.measured = parameters[0]
  self.calculated = parameters[1]

  // Chart configuration starts here
  self.index = 90
  self.chartElementSelectors = [
    { selector: '#model-filament-speed', chart: null }
  ]
  self.chartData = [
    createDataSeries(self.measured.label, self.index, 0, self.measured.unit()),
    createDataSeries(self.calculated.label, self.index, 0, self.calculated.unit())
  ]

  /**
   * Update the data series and redraw the chart
   */

  self.updateChart = () => {
    self.index++
    pushToDataSeries(self, 0, self.measured.valueFormatted()),
    pushToDataSeries(self, 1, self.calculated.valueFormatted())
    updateChart(self)
  }

  /**
   * Start the interval timer once everything is loaded
   */

  self.onStartupComplete = () => setInterval(() => self.updateChart(), 100)
}

$(function () {
  OCTOPRINT_VIEWMODELS.push({
    construct: CombinedFilamendSpeedViewModel,
    dependencies: [
      'filamentSpeedViewModel',
      'virtualFilamentSpeedViewModel'
    ]
  })

  OCTOPRINT_VIEWMODELS.push({
    construct: CombinedTemperatureViewModel,
    dependencies: [
      'filamentTemperatureViewModel',
      'filamentPyrometerTemperatureViewModel',
      'temperatureViewModel'
    ]
  })

  OCTOPRINT_VIEWMODELS.push({
    construct: CombinedTimingViewModel,
    dependencies: [
      'heaterOntimeViewModel',
      'heaterOfftimeViewModel'
    ]
  })

  OCTOPRINT_VIEWMODELS.push({
    construct: CombinedPowerSensorViewModel,
    dependencies: [
      'heaterPowerReflectedViewModel',
      'heaterPowerForwardViewModel'
    ]
  })
})
