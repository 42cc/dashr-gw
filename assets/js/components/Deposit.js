import React from "react";
import DjangoCSRFToken from 'django-react-csrftoken';
import Button from 'react-bootstrap/lib/Button';
import Panel from 'react-bootstrap/lib/Panel';
import Form from 'react-bootstrap/lib/Form';
import FormGroup from 'react-bootstrap/lib/FormGroup';
import FormControl from 'react-bootstrap/lib/FormControl';
import ControlLabel from 'react-bootstrap/lib/ControlLabel';
import HelpBlock from 'react-bootstrap/lib/HelpBlock';
import Col from 'react-bootstrap/lib/Col';
import InputGroup from 'react-bootstrap/lib/InputGroup';

export default class DepositDash extends React.Component {
    render() {
        if (this.state && this.state.dashWallet && this.state.statusUrl) {
            return (
                <Panel bsStyle="default" className="panel-wrapper panel-wrapper-container">
                    <Col sm={12} md={6}>
                        <b>You have initiated a transaction from Dash to Ripple</b>
                        <p>
                            <span>Please transfer your Dash coins to this address:</span>
                            {' '}
                            <b>{this.state.dashWallet}</b>
                        </p>
                        <p>
                            You can track status of this transaction
                            {' '}
                            <a href={this.state.statusUrl}>here</a>.
                        </p>
                    </Col>
                </Panel>
            )
        }
        return (
            <Panel header="Deposit DASH to Ripple" bsStyle="default"
                   className="panel-wrapper panel-wrapper-container">
                <Col sm={12} md={6}>
                    <Form onSubmit={this.handleFormSubmit.bind(this)} id="deposit-form">
                        <DjangoCSRFToken/>
                        <FormGroup controlId="id_ripple_address">
                            <Col md={12}>
                                <ControlLabel>Enter your ripple address, please:</ControlLabel>
                                <InputGroup>
                                    <FormControl type="text" name="ripple_address"/>
                                    <InputGroup.Button>
                                        <Button type="submit">Start</Button>
                                    </InputGroup.Button>
                                </InputGroup>
                                {this.getRippleAddressError()}
                                <FormControl.Feedback />
                                <HelpBlock>
                                    <Button bsStyle="link" href="/deposit/how-to/">
                                        Need help?
                                    </Button>
                                </HelpBlock>
                            </Col>
                        </FormGroup>
                    </Form>
                </Col>
            </Panel>
        );
    }

    handleFormSubmit(event) {
        event.preventDefault();
        $('button[type="submit"]').prop('disabled', true);
        $.post(
            urls.submitDeposit,
            $('#deposit-form').serialize(),
        ).done((data) => {
            if (data.success) {
                this.setState({
                    dashWallet: data['dash_wallet'],
                    statusUrl: data['status_url'],
                });
            } else {
                $('#deposit-form .form-group').addClass('has-error');
                this.setState({rippleAddressError: data['ripple_address_error']});
            }
        }).always(() => {$('button[type="submit"]').prop('disabled', false);})
    }

    getRippleAddressError() {
        if (this.state && this.state.rippleAddressError) {
            return (
                <HelpBlock>{this.state.rippleAddressError}</HelpBlock>
            );
        }
    }
}
