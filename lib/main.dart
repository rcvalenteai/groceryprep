import 'package:flutter/material.dart';
import 'homewidget.dart';
import 'test'

void main() => runApp(App());

class App extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'My Flutter App',
      home: Home(),
    );
  }
}

class Home extends StatefulWidget {
  @override
  State<StatefulWidget> createState() {
    return _HomeState();
  }
}
//
// class _HomeState extends State<Home> {
//   @override
//   Widget build(BuildContext context) {
//     return Scaffold(
//       appBar: AppBar(
//         title: Text('My Flutter App'),
//       ),
//       bottomNavigationBar: BottomNavigationBar(
//         currentIndex: 0, // this will be set when a new tab is tapped
//         items: [
//           BottomNavigationBarItem(
//             icon: new Icon(Icons.home),
//             title: new Text('Home'),
//           ),
//           BottomNavigationBarItem(
//             icon: new Icon(Icons.mail),
//             title: new Text('Messages'),
//           ),
//           BottomNavigationBarItem(
//               icon: Icon(Icons.person),
//               title: Text('Profile')
//           )
//         ],
//       ),
//     );
//   }
// }