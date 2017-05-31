import React from 'react';
import ReactDOM from 'react-dom';

class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            slug: '/'
        };
    }

    render() {
        let slug = 'about';

        if (slug === '/') {
            return (<Landing />);
        } else {
            return (<Page slug={slug}/>);
        }
    }
}

class Landing extends React.Component {
    render() {
        return null;
    }
}

class Page extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            page: null
        };
    }

    loadPage() {
        $.ajax({
            url: this.props.slug,
            dataType: 'json',
            cache: false,
            success: function (data) {
                this.setState({page: JSON.parse(data)[0]});
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(status, err);
            }.bind(this)
        });
    }

    componentDidMount() {
        this.loadPage();
    }

    render() {
        let page = this.state.page,
            pageTempate = <p>Page does not exists</p>;

        if (page !== null) {
            pageTempate = (
                <div dangerouslySetInnerHTML={{__html: page.fields.description}}/>
            )
        }
        return pageTempate;
    }
}

const container = document.getElementById('container');
ReactDOM.render(<App />, container);