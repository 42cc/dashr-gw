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
        if (this.state && this.state.rippleAddress && this.state.statusUrl) {
            return (
                <Panel bsStyle="default" className="panel-wrapper panel-wrapper-container">
                    <Col sm={12} md={6}>
                        <b>You have initiated a transaction from Ripple to Dash</b>
                        <p>
                            <span>Please transfer your Ripple tokens to this address:</span>
                            {' '}
                            <b>{this.state.rippleAddress}</b>
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
            <Panel header="Withdraw DASH from Ripple" bsStyle="default"
                   className="panel-wrapper panel-wrapper-container">
                <Col sm={12} md={6}>
                    <Form onSubmit={this.handleFormSubmit.bind(this)} id="withdrawal-form">
                        <DjangoCSRFToken/>
                        <FormGroup controlId="id_dash_address">
                            <Col md={12}>
                                <ControlLabel>Enter your dash address, please:</ControlLabel>
                                <InputGroup>
                                    <FormControl type="text" name="dash_address"/>
                                    <InputGroup.Button>
                                        <Button type="submit">Start</Button>
                                    </InputGroup.Button>
                                </InputGroup>
                                {this.getDashAddressError()}
                                <FormControl.Feedback />
                                <HelpBlock>
                                    <Button bsStyle="link" href="/withdraw/how-to/">Need help?</Button>
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
            urls.submitWithdrawal,
            $('#withdrawal-form').serialize(),
        ).done((data) => {
            if (data.success) {
                this.setState({
                    rippleAddress: data['ripple_address'],
                    destinationTag: data['destination_tag'],
                    statusUrl: data['status_url'],
                });
            } else {
                $('#deposit-form .form-group').addClass('has-error');
                this.setState({dashAddressError: data['dash_address_error']});
            }
        }).always(() => {$('button[type="submit"]').prop('disabled', false);})
    }

    getDashAddressError() {
        if (this.state && this.state.dashAddressError) {
            return (
                <HelpBlock>{this.state.dashAddressError}</HelpBlock>
            );
        }
    }
}
