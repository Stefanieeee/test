/*
 * View model for OctoPrint-ARGCODE
 *
 * Author: Christian Loelkes
 * License: AGPLv3
 */

function ThreeJSViewModel (parameters) {

   var self = this;
   self.printerProfiles = parameters[0]

   self.toolPosition = {
     x: ko.observable(),
     y: ko.observable(),
     z: ko.observable(),
     feedrate: ko.observable()
   }

  self.setUpBedVisualization = (xdim, ydim) => {
    let bed = self.scene.getObjectByName('bed-edges')
    if (bed !== undefined) {
      self.scene.remove(bed)
      console.log('Remove existing bed')
    }
    const geometry = new THREE.PlaneGeometry( ydim, xdim, 32 )
    const edges = new THREE.EdgesGeometry( geometry )
    let line = new THREE.LineSegments( edges, new THREE.LineBasicMaterial( { color: 0x000000 } ) )
    line.name = 'bed-edges'
    line.translateY(xdim/2)
    line.translateX(ydim/2)
    self.scene.add( line )
  }

   self.setUpToolVisualization = () => {

     let color = 0x000000
     let length = 20
     let headLength = 1 * length
     let headWidth = 0.4 * headLength

     let dir = new THREE.Vector3(0,0,-1)
     dir.normalize()

     self.toolHelper = new THREE.ArrowHelper(dir, self.currentPosition, length, color, headLength, headWidth)
     self.updateToolPosition()
     self.scene.add(self.toolHelper)

   }

   self.updateToolPosition = () => {

     let newPosition = self.currentPosition.clone()
     newPosition.add( new THREE.Vector3(0, 0, 20) )
     self.toolHelper.position.copy(newPosition)

   }

   self.init = () => {

     self.currentPosition = new THREE.Vector3(0, 0, 0)

     // Set up the scene
     self.scene = new THREE.Scene()
     self.GCODEGroup = new THREE.Group()
     self.scene.add(self.GCODEGroup)

     // self.setUpToolVisualization()
     self.printerProfiles.currentProfileData.subscribe(newProfileData => {
       self.setUpBedVisualization(newProfileData.volume.width(), newProfileData.volume.depth())
     })

     // Set up camera
     self.camera = new THREE.PerspectiveCamera( 50, 1, 1, 5000 )
     self.camera.up.set( 0, 0, 1 );
     self.camera.position.set( 50, -100, 50 )

     // Set up renderer
     self.renderer = new THREE.WebGLRenderer({
       canvas: document.querySelector('#argcode canvas')
     })
     self.renderer.setPixelRatio( window.devicePixelRatio * 2 )
     self.renderer.setClearColor( 0xffffff, 1);
     self.controls = new THREE.OrbitControls( self.camera, self.renderer.domElement )
     self.controls.addEventListener( 'change', self.render ) // use if there is no animation loop
     self.controls.minDistance = 10
     self.controls.maxDistance = 1000
     self.controls.target = new THREE.Vector3(50,50,0)
     self.controls.update()

   }

   self.render = () => self.renderer.render( self.scene, self.camera )

   self.resize = container => {

     self.camera.aspect = container.clientWidth / container.clientHeight
     self.camera.updateProjectionMatrix()
     self.renderer.setSize( container.clientWidth, container.clientHeight )

   }

   self.setUpHelpers = () => {

     // Set up the grid
     const gridHelper = new THREE.GridHelper( 1000, 200 );
     gridHelper.material.transparent = true
     gridHelper.material.opacity = 0.2
     gridHelper.rotateX( -Math.PI/2 )
     // gridHelper.position.add( new THREE.Vector3( 125, 125, 0) )
     self.scene.add( gridHelper );

     // Set up the axes
     const axesHelper = new THREE.AxesHelper( 50 );
     self.scene.add( axesHelper );

   }

   self._drawLine = (from, to) => {

     const material = new THREE.LineBasicMaterial( { color: 0x000000 } );
     const geometry = new THREE.BufferGeometry().setFromPoints( [ from, to ] );
     const line = new THREE.Line( geometry, material );
     self.GCODEGroup.add( line )

   }

   self.reset = () => {

     self.currentPosition.copy( new THREE.Vector3(0, 0, 0) )
     while (self.GCODEGroup.children.length) {
       self.GCODEGroup.remove(self.GCODEGroup.children[0])
     }

   }

   self.onPositionUpdate = data => {

     self.toolPosition.x( data.x )
     self.toolPosition.y( data.y )
     self.toolPosition.z( data.z )
     self.toolPosition.feedrate( data.feedrate )

     const newPosition = new THREE.Vector3( data.x, data.y, data.z )
     self._drawLine( self.currentPosition, newPosition )
     self.currentPosition.copy( newPosition )
     // self.updateToolPosition()

   }

   self.animate = () => {

     self.render()
     requestAnimationFrame( self.animate );

   }

   self.onStartupComplete = () => {

     self.init()
     self.setUpHelpers()

     self.onDataUpdaterPluginMessage = (id, message) => {
       if (id === 'argcode_position_update') self.onPositionUpdate(message)
       if (id === 'argcode_reset') self.reset()
       self.render()
     }

   }

}

$(function () {

  OCTOPRINT_VIEWMODELS.push({
    construct: ThreeJSViewModel,
    elements: ['#argcode_controls'],
    dependencies: ['printerProfilesViewModel']
  })

})
