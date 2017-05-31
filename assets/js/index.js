import React from 'react';
import ReactDOM from 'react-dom';
import Button from 'react-bootstrap/lib/Button';
import Panel from 'react-bootstrap/lib/Panel';

class Landing extends React.Component {
    render() {
        return (
            <Panel bsStyle="default" className="main-menu-wrapper text-center">
                <Button bsStyle="default" className="btn-landing" href="#">
                    Deposit DASH to Ripple
                </Button>
                <Button bsStyle="default" className="btn-landing" href="#">
                    Withdraw DASH from Ripple
                </Button>
            </Panel>
        );
    }
}

ReactDOM.render(<Landing />, document.getElementById('container'));