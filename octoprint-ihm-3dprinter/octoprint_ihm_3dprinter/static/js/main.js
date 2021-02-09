var PLUGIN_UID = 'ihm_3dprinter'
var PLUGIN_TAB = `#tab_plugin_${PLUGIN_UID}`

var PLOT_BASE_OPTIONS = {
  yaxis: {
    min: 0,
    show: true,
    tickFormatter: (value, axis) => '',
    ticks: 10
  },
  xaxis: {
    show: true,
    tickFormatter: (value, axis) => '',
    tickSize: 10
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


/////

function PluginNavbarStatusViewModel (parameters) {
  var self = this
  self.mcs = parameters[0]
  self.items = [
    {
      label: 'HPG Temp.',
      value: self.mcs.heater.temperature.valueFormatted,
      unit: self.mcs.heater.temperature.unit
    },
    {
      label: 'HPG Power Forw.',
      value: self.mcs.heater.power_forward.valueFormatted,
      unit: self.mcs.heater.power_forward.unit
    },
    {
      label: 'HPG Power Refl.',
      value: self.mcs.heater.power_reflected.valueFormatted,
      unit: self.mcs.heater.power_reflected.unit
    }
  ]
}

$(function () {
  OCTOPRINT_VIEWMODELS.push({
    construct: PluginNavbarStatusViewModel,
    dependencies: ['microwaveControlViewModel'],
    elements: ['#navbar_plugin_ihm_3dprinter'],
  })
})


function PluginNotificationViewModel (parameters) {
  var self = this
  self.octoprint_announcements = parameters[0]

  self.error_channel = {
    channel: 'Plugin Error',
    key: '_' + PLUGIN_UID + '_error',
    priority: 1,
    data: []
  }
  self.info_channel = {
    channel: 'Plugin Info',
    key: '_' + PLUGIN_UID + '_info',
    priority: 2,
    data: []
  }

  self.info = (title, body) => {
    self.display('info', title, body)
  }

  self.error = (title, body) => {
    self.display('error', title, body)
  }

  self.display = (channel, title, body) => {
    const message = {
      read: false,
      link: '',
      title: title,
      summary_without_images: body,
      published: Math.floor(Date.now() / 1000)
    }
    if ( channel === 'error' ) {
      self.error_channel.data.push(message)
    } else if ( channel === 'info' ) {
      self.info_channel.data.push(message)
    } else {
      return
    }
    if (self.octoprint_announcements === null) return
    self.octoprint_announcements.displayAnnouncements([self.info_channel, self.error_channel])
  }

  self.onDataUpdaterPluginMessage = (id, message) => {
    if (id !== PLUGIN_UID + '_notification') return
    console.log(message)
    if (message.error !== undefined) {
      message.error.forEach(item => self.error(item.title, item.body))
    }
    if (message.info != undefined) {
      message.info.forEach( item => self.info(item.title, item.body))
    }
  }
}

$(function () {
  OCTOPRINT_VIEWMODELS.push({
    construct: PluginNotificationViewModel,
    dependencies: ['announcementsViewModel'],
    optional: ['announcementsViewModel']
  })
})

///

function PluginViewSelectorViewModel (parameters) {
  var self = this
  self.printerState = parameters[0]
  self.current_tab_selector = '.overviewContainer'

  self.printerState.isOperational.subscribe(newState => {
    if(newState === true) {
      self.show(self.current_tab_selector)
      $('#pluginViewSelector').show()
      $('#microwaveStatus').show()
    } else {
      self.show('.printerNotConnectedContainer')
      $('#pluginViewSelector').hide()
      $('#microwaveStatus').hide()
    }
  })

  self.show = tabSelector => {
    $('.pluginViewContainer').hide()
    $(tabSelector).show()
  }
}

function ManualControlViewModel (parameters) {
  var self = this
  self.octoprint_control = parameters[0]
  self.microwave_control = parameters[1]
  self.frequency = parameters[2]
  self.offtime = parameters[3]
  self.power = parameters[4]
  self.ontime = parameters[5]
  self.connection = self.microwave_control.heater.connection
  self.mode = self.microwave_control.heater.mode
  self.setMode = self.microwave_control.heater.setMode
}

function PresetControlViewModel (parameters) {
  var self = this
  self.octoprint_control = parameters[0]
  self.microwave_control = parameters[1]
}

$(function () {
  OCTOPRINT_VIEWMODELS.push({
    construct: ManualControlViewModel,
    dependencies: [
      'controlViewModel',
      'microwaveControlViewModel',
      'heaterFrequencyViewModel',
      'heaterOfftimeViewModel',
      'heaterPowerViewModel',
      'heaterOntimeViewModel'
    ],
    elements: ['#manualControlMode']
  })

  OCTOPRINT_VIEWMODELS.push({
    construct: PluginViewSelectorViewModel,
    elements: ['#pluginViewSelector'],
    dependencies: ['printerStateViewModel']
  })
})
