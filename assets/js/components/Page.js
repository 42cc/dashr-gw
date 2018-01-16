import React from "react";
import Panel from 'react-bootstrap/lib/Panel';
import Col from 'react-bootstrap/lib/Col';


export default class Page extends React.Component {
    loadPage(slug) {
        $.get(slug).done(data => {this.setState({page: data.page})});
    }

    componentDidMount(){
        this.loadPage(this.props.match.url);
    }

    render() {
        if (!this.state || this.state.page === 'undefined') {
            return 'Page does not exists';
        } else if (this.props.isWrapped) {
            return (
                <Panel className="panel-wrapper panel-wrapper-container">
                    <Panel.Heading>{this.state.page.title}</Panel.Heading>
                    <Panel.Body>
                        <Col sm={12}>
                            <div dangerouslySetInnerHTML={{__html: this.state.page.description}}/>
                        </Col>
                    </Panel.Body>
                </Panel>
            );
        } else {
            return <div dangerouslySetInnerHTML={{__html: this.state.page.description}}/>;
        }
    }
}
