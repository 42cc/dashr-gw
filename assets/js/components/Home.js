import React from "react";
import Button from 'react-bootstrap/lib/Button';
import Panel from 'react-bootstrap/lib/Panel';
import queryString from 'query-string';

export default class Home extends React.Component {
    componentDidMount() {
        // rediret to next param
        const search = this.props.location.search;
        const params = queryString.parse(search);
        if (params) this.props.history.push(params['next']);
    }

    render() {
        return (
            <Panel bsStyle="default" className="panel-wrapper panel-wrapper-main-menu">
                <Button bsStyle="default" className="btn-landing" href="/deposit-dash/">
                    Deposit DASH to Ripple
                </Button>
                <Button bsStyle="default" className="btn-landing" href="/withdraw-dash/">
                    Withdraw DASH from Ripple
                </Button>
            </Panel>
        );
    }
}
