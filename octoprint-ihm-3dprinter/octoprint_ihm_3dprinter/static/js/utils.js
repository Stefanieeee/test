var setUpSensor = function(self) {
  self.available = ko.observable(false)
  self.rangeError = ko.observable(false)

  self.coefficient = ko.observable()
  self.newCoefficient = ko.observable()
  self.newCoefficient.extend({ notify: 'always' })
  self.coefficient.subscribe(newValue => {
    if (self.newCoefficient() === undefined) {
      self.newCoefficient(newValue)
    }
  })
  self.newCoefficientValid = ko.observable(false)
  self.newCoefficient.subscribe(newValue => {
    if (!isNaN(newValue) && newValue !== '') {
      self.newCoefficientValid(true)
    } else {
      self.newCoefficientValid(false)
    }
  })

  /**
   * Change the coefficient through a GCODE command
   *
   * @param {String} gcode_cmd - The GCODE command, e.g. M1020
   * @param {String} id - The sensor id
   * @param {Number} value - Override the newCoefficient with this
   */

  self.setCoefficient = (gcode_cmd, id, value) => {

    if (self.octoprint_control === undefined) {
      console.error('Cannot access octoprint control!')
      return
    }

    if (gcode_cmd === undefined || isNaN(id)) {
      console.error('gcode_cmd and id are required!')
      return
    }

    if (value !== undefined) {
      self.newCoefficient(value)
    }

    if (self.newCoefficientValid()) {
      const payload = { command: `${gcode_cmd} P${id} S${self.newCoefficient()}` }
      self.octoprint_control.sendCustomCommand(payload)
      console.info(`Send ${payload.command}`)
    } else {
      console.error('New coefficient cannot be set')
    }
  }

  self.offset = ko.observable()
  self.newOffset = ko.observable()
  self.newOffset.extend({ notify: 'always' })
  self.offset.subscribe(newValue => {
    if (self.newOffset() === undefined) {
      self.newOffset(newValue)
    }
  })
  self.newOffsetValid = ko.observable(false)
  self.newOffset.subscribe(newValue => {
    if (!isNaN(newValue) && newValue !== '') {
      self.newOffsetValid(true)
    } else {
      self.newOffsetValid(false)
    }
  })

  /**
   * Change the offset through a GCODE command
   *
   * @param {String} gcode_cmd - The GCODE command, e.g. M1020
   * @param {String} id - The sensor id
   * @param {Number} value - Override the newOffset with this
   */

  self.setOffset = (gcode_cmd, id, value) => {

    if (self.octoprint_control === undefined) {
      console.error('Cannot access octoprint control!')
      return
    }

    if (gcode_cmd === undefined || isNaN(id)) {
      console.error('gcode_cmd and id are required!')
      return
    }

    if (value !== undefined) {
      self.newOffset(value)
    }

    if (self.newOffsetValid()) {
      const payload = { command: `${gcode_cmd} P${id} S${self.newOffset()}` }
      self.octoprint_control.sendCustomCommand(payload)
      console.info(`Send ${payload.command}`)
    } else {
      console.error('New offset cannot be set')
    }
  }

}

/**
 * Set up the value precision formatting
 *
 * @param {Object} self - The object holding the value
 * @param {number} precision - The amount of floating point numbers to display
 */

var setUpValuePrecision = function (self, precision = 3) {
  self.precision = ko.observable(precision)
  self.valueFormatted = ko.computed(function () {
    if(isNaN(self.value()) || self.value() === null) {
      return self.value()
    } else {
      return self.value().toFixed(self.precision())
    }
  })
}

/**
 * Add data to a certain data series
 *
 * @param {Object} self - The object containing the chart data
 * @param {number} id - The id of the series
 * @param {number} value - The value to add
 *
 */

var pushToDataSeries = function(self, id, value) {
  self.chartData[id].data.push([self.index, value])
  self.chartData[id].data.shift()
}

/**
 * Update the sharts and draw them if visible
 *
 * @param {Object} self - The object containing the graphs
 *
 */

var updateChart = self => {
  for (let item of self.chartElementSelectors) {
    if ($(item.selector).is(':visible')) {
      if (item.chart === null) {
        if (item.options === undefined) {
          item.options = PLOT_BASE_OPTIONS
        }
        item.chart = $.plot($(item.selector), [[]], item.options)
      }
      item.chart.setData(self.chartData)
      item.chart.setupGrid()
      item.chart.draw()
    }
  }
}

/**
 * Create a new data series object
 *
 * @param {string} label - The label to display in the legen
 * @param {number} length - The data lenght of the data series
 * @param {string} color - A css style color string
 * @param {string} unit - Unit to be displayed next to the value
 *
 */

var createDataSeries = function(label = '', length = 60, color = 'rgb(0, 0, 0)', unit='') {

  // Creaty an empty data series
  let emptyData = []
  for (var i = 0; i < length; i++) {
    emptyData.push([i, null])
  }

  let series = {
    color: color,
    data: emptyData,
    label: label,
    // lines: specific lines options
    // bars: specific bars options
    // points: specific points options
    // xaxis: number
    // yaxis: number
    clickable: false,
    hoverable: false,
    // shadowSize: number
    // highlightColor: color or number
    unit: unit
  }
  return series

}

/**
 * Set up the basic value elements
 *
 * @param {Object}
 */

var setUpValue = function (self, unit = '', name = 'Value') {
  self.name = name
  self.value = ko.observable()
  self.unit = ko.observable(unit)
  self.value.extend({ notify: 'always' })
  self.newValue = ko.observable()

  self.value.subscribe(newValue => {
    if (self.newValue() === undefined) {
      self.newValue(newValue)
    }
  })
}

var setUpValuePlot = function (self, label, selector, length = 60) {
  self.label = label
  self.chartElementSelectors = [
    {selector: selector, chart: null}
  ]
  self.index = length

  self.chartData = [
    createDataSeries(label, length, 0, self.unit())
  ]

  self.onStartupComplete = () => setInterval(() => {
    self.index++
    pushToDataSeries(self, 0, self.value())
    updateChart(self)
  }, 100)
}

/**
 * Set up the containers and checks for minimum and maximum values
 * @param {Object} self - The object to work on
 * @param {number} minimum - The minimum value
 * @param {number} maximum - The maximum value
 */

var setUpMinMaxValue = (self, minimum, maximum) => {
  self.newValueValid = ko.observable(false)
  self.limitsValid = ko.observable(false)
  // Set up minimum values
  self.minimum = ko.observable(minimum)
  self.minimum.extend({ notify: 'always' })
  self.minimum.subscribe(newValue => {
    if (self.newMinimum() === undefined) {
      self.newMinimum(newValue)
    }
  })

  self.newMinimum = ko.observable()

  self.newMinimum.subscribe(newMinimum => {
    if (newMinimum == '' || self.maximum() === null) {
      self.limitsValid(true)
    } else if (isNaN(newMinimum)) {
      self.limitsValid(false)
      console.error(`Minimum ${newMinimum} must be a number.`)
    } else if (newMinimum >= self.maximum()) {
      self.limitsValid(false)
      console.error(`Minimum ${newMinimum} must be smaller than the maximum (${self.maximum()}).`)
    } else {
      self.limitsValid(true)
    }
  })
  // Set up maximum values

  self.maximum = ko.observable(maximum)
  self.maximum.extend({ notify: 'always' })
  self.maximum.subscribe(newValue => {
    if (self.newMaximum() === undefined) {
      self.newMaximum(newValue)
    }
  })

  self.newMaximum = ko.observable()
  self.newMaximum.subscribe(newMaximum => {
    if (newMaximum == '' || self.minimum() === null) {
        self.limitsValid(true)
    } else if (isNaN(newMaximum)) {
      self.limitsValid(false)
      console.error(`Maximum ${newMaximum} must be a number.`)
    } else if (newMaximum <= self.minimum()) {
      self.limitsValid(false)
      console.error(`Maximum ${newMaximum} must be larger than the minimum (${self.maximum()}).`)
    } else {
      self.limitsValid(true)
    }
  })

  self.newValue.subscribe(newValue => {
    // Value is not a number?
    if (isNaN(newValue)) {
      console.error(`${self.name} ${newValue} is not a number.`)
      self.newValueValid(false)
      return
    }

    // Do nothing if neither minimum nor maximum are set
    if (isNaN(self.minimum()) && isNaN(self.maximum())) {
      self.newValueValid(true)
      return
    }

    // True if minimum is set and value is below minimum
    const check_min = !isNaN(self.minimum()) && newValue >= self.minimum()
    // True if maximum is set and value is above minimum
    const check_max = !isNaN(self.maximum()) && newValue <= self.maximum()
    // Only check minimum if maximum is not set and set value

    if (check_min && isNaN(self.maximum())) {
      self.newValueValid(true)
    // Only check maximum if minimum is not set and set value
    } else if (check_max && isNaN(self.minimum())) {
      self.newValueValid(true)
    // Check maximum and minimum and set value
    } else if (check_min && check_max) {
      self.newValueValid(true)
    } else {
      console.error(`${self.name} must be in range ${self.minimum()}-${self.maximum()}`)
      self.newValueValid(false)
    }
  })

  self.setMinimum = (gcode_cmd, id) => {

    if (self.octoprint_control === undefined) {
      console.error('Cannot access octoprint control!')
      return
    }

    if (gcode_cmd === undefined || isNaN(id)) {
      console.error('gcode_cmd and id are required!')
      return
    }

    if (self.limitsValid()) {
      const limitValueCmd = self.newMinimum() ? `S${self.newMinimum()}` : ''
      const payload = { command: `${gcode_cmd} P${id} ${limitValueCmd}` }
      self.octoprint_control.sendCustomCommand(payload)
      console.info(`Send ${payload.command}`)
    } else {
      console.error('Cannot set new minimum limit!')
    }

  }

  self.setMaximum = (gcode_cmd, id) => {

    if (self.octoprint_control === undefined) {
      console.error('Cannot access octoprint control!')
      return
    }

    if (gcode_cmd === undefined || isNaN(id)) {
      console.error('gcode_cmd and id are required!')
      return
    }

    if (self.limitsValid()) {
      const limitValueCmd = self.newMaximum() ? `S${self.newMaximum()}` : ''
      const payload = { command: `${gcode_cmd} P${id} ${limitValueCmd}` }
      self.octoprint_control.sendCustomCommand(payload)
      console.info(`Send ${payload.command}`)
    } else {
      console.error('Cannot set new maximum limit!')
    }

  }

}
