import React from "react";
import Panel from 'react-bootstrap/lib/Panel';
import Col from 'react-bootstrap/lib/Col';


export default class Page extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            page: null
        };
    }

    loadPage(slug) {
        $.ajax({
            url: slug,
            dataType: 'json',
            cache: false,
            success: function (response) {
                if (response.success) {
                    this.setState({page: response.page});
                }
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(status, err);
            }.bind(this)
        });
    }

    componentDidMount(){
        this.loadPage(this.props.match.url);
    }
    componentWillReceiveProps(props) {
        this.loadPage(props.match.url);
    }

    render() {
        let page = this.state.page,
            wrapped = this.props.wrapped,
            pageTempate;

        if (wrapped == 'true' & page !== null) {
            pageTempate = (
                <Panel className="panel-wrapper panel-wrapper-container">
                    <Panel.Heading>{page.title}</Panel.Heading>
                    <Panel.Body>
                        <Col sm={12}>
                            <div dangerouslySetInnerHTML={{__html: page.description}}/>
                        </Col>
                    </Panel.Body>
                </Panel>
            )
        } else if (page !== null & wrapped == 'false') {
            pageTempate = (
                <div dangerouslySetInnerHTML={{__html: page.description}}/>
            )
        } else {
            pageTempate = <p>Page does not exists</p>
        }

        return pageTempate;
    }
}
