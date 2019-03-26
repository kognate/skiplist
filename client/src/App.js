import React, { Component } from 'react';
import './App.css';
import Slider from "react-slick";

const SlideRow = (props) => {
    return (<tr key={props.type}>
	    <td>{props.type}</td>
	    <td>{props.age}</td>
	    <td>{props.quantity}</td></tr>);
};

const HeaderArrow = (props) => {
	if (props.direction === "down") {
		return (<span>{props.title} &darr;</span>)
	} else if (props.direction === "up") {
		return (<span>{props.title} &uarr;</span>)
	} else {
		return (<span>{props.title}</span>)
	}
};


class DataTable extends React.Component {
	state = { sort_direction: "", sort_field: 0, dogs: []};

	constructor(props) {
		super(props);
		this.state = {
			sort_direction: "",
			sort_field: 0,
			dogs: props.canines
		};
	}

	sortDogs(idx) {
		let tosort = [...this.state.dogs];
		tosort.sort((a,b) => {
			if (a[idx] > b[idx]) {
				return this.state.sort_direction === "down" ? -1 : 1;
			} else if (a[idx] === b[idx]) {
				return this.state.sort_direction === "down" ? 0 : 0;
			} else {
				return this.state.sort_direction === "down" ? 1 : -1;
			}
		});
		this.setState({sort_field: idx, dogs: tosort, sort_direction: this.state.sort_direction === "up" ? "down" : "up"});
	}
    render() {
	return (<div>
		<table>
			<thead>
			<tr>
				<td onClick={() => this.sortDogs(0)}>
					<HeaderArrow title="Type" direction={ this.state.sort_field === 0 ? this.state.sort_direction : ""}/></td>
				<td onClick={() => this.sortDogs(1)}>
					<HeaderArrow title="Age" direction={ this.state.sort_field === 1 ? this.state.sort_direction : ""}/></td>
				<td onClick={() => this.sortDogs(2)}>
					<HeaderArrow title="Quantity" direction={ this.state.sort_field === 2 ? this.state.sort_direction : ""}/></td>
			</tr>
	    </thead>
	    <tbody>
		{this.state.dogs.map(x => <SlideRow key={x[0]} type={x[0]}
											age={x[1]}
											quantity={x[2]}/>)}
		</tbody>
	    </table>
	    </div>);
    }

}

const Slide = (props) => {
    return (
	<div className="Slide-container">
	    <h3>{props.item.title}</h3>
	<img alt={props.item.title} src={props.item.img_url}/>
	<DataTable canines={props.item.canines}/>
	</div>);
};

class SimpleSlider extends React.Component {
    state = { slides: [] };

    componentDidMount() {
	fetch('/api/dogs').then((res) => {
	    res.json().then((json) => {
		this.setState({slides: json});
	    })});
    }

  render() {
    var settings = {
	dots: true,
	infinite: true,
	speed: 500,
	slidesToShow: 1,
	slidesToScroll: 1,
    };
      
    return (
      <Slider {...settings}>
	    {this.state.slides.map(x => <Slide key={x.title} item={x}/>)}
      </Slider>
    );
  }
};

class App extends Component {
  render() {
    return (
      <div className="App">
	    <SimpleSlider/>
      </div>
    );
  }
}

export default App;
