import * as THREE from './three/three.module.js';
import Stats from './three/stats.module.js';
import { TrackballControls } from './three/TrackballControls.js';
import { PCDLoader } from './three/PCDLoader.js';

var container, stats;
var camera, controls, scene, renderer;

init();
animate();

function init() {

    scene = new THREE.Scene();
    scene.background = new THREE.Color( 0x000000 );

    camera = new THREE.PerspectiveCamera( 15, window.innerWidth / window.innerHeight, 0.01, 40 );
    camera.position.x = 0.4;
    camera.position.z =  -2;
    camera.up.set( 0, 0, 1 );

    scene.add( camera );

    renderer = new THREE.WebGLRenderer( { antialias: true } );
    renderer.setPixelRatio( window.devicePixelRatio );
    renderer.setSize( window.innerWidth, window.innerHeight );
    document.body.appendChild( renderer.domElement );

    var loader = new PCDLoader();
    loader.load( 'example.pcd', function ( points ) {

        scene.add( points );
        var center = points.geometry.boundingSphere.center;
        controls.target.set( center.x, center.y, center.z );
        controls.update();

        var points = scene.getObjectByName( 'example.pcd' );
        points.material.size *= 12;

    } );

    container = document.createElement( 'div' );
    document.body.appendChild( container );
    container.appendChild( renderer.domElement );

    controls = new TrackballControls( camera, renderer.domElement );

    controls.rotateSpeed = 2.0;
    controls.zoomSpeed = 0.3;
    controls.panSpeed = 0.2;

    controls.noZoom = false;
    controls.noPan = false;

    controls.staticMoving = true;
    controls.dynamicDampingFactor = 0.3;

    controls.minDistance = 10;
    controls.maxDistance = 0.3 * 100;

    stats = new Stats();
    container.appendChild( stats.dom );

   // fitCameraToSelection( camera, controls, points)

    window.addEventListener( 'resize', onWindowResize, false );

    window.addEventListener( 'keypress', keyboard );

}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize( window.innerWidth, window.innerHeight );
    controls.handleResize();
}
function fitCameraToSelection( camera, controls, selection, fitOffset = 1.2 ) {
  const box = new THREE.Box3();

   for( const object of selection ) box.expandByObject( object );


  const size = box.getSize( new THREE.Vector3() );
  const center = box.getCenter( new THREE.Vector3() );

  const maxSize = Math.max( size.x, size.y, size.z );
  const fitHeightDistance = maxSize / ( 2 * Math.atan( Math.PI * camera.fov / 360 ) );
  const fitWidthDistance = fitHeightDistance / camera.aspect;
  const distance = fitOffset * Math.max( fitHeightDistance, fitWidthDistance );

  const direction = controls.target.clone()
    .sub( camera.position )
    .normalize()
    .multiplyScalar( distance );
  console.log(distance)
  controls.maxDistance = distance * 10;
  controls.target.copy( center );

  camera.near = distance / 100;
  camera.far = distance * 100;
  camera.updateProjectionMatrix();

  camera.position.copy( controls.target ).sub(direction);

  controls.update();

}

function keyboard( ev ) {

    var points = scene.getObjectByName( 'example.pcd' );

    switch ( ev.key || String.fromCharCode( ev.keyCode || ev.charCode ) ) {

        case '+':
            points.material.size *= 1.2;
            points.material.needsUpdate = true;
            break;

        case '-':
            points.material.size /= 1.2;
            points.material.needsUpdate = true;
            break;

        case 'c':
            points.material.color.setHex( Math.random() * 0xffffff );
            points.material.needsUpdate = true;
            break;
    }
}

function animate() {
    requestAnimationFrame( animate );
    controls.update();
    renderer.render( scene, camera );
    stats.update();

}
