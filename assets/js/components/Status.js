import React from "react";
import Col from 'react-bootstrap/lib/Col';
import Panel from 'react-bootstrap/lib/Panel';
import Table from 'react-bootstrap/lib/Table';

export default class Status extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            transactionData: {},
        };
    }

    render() {
        const transactionData = this.state.transactionData;
        const stateHistory = transactionData.stateHistory || [];
        if ($.isEmptyObject(transactionData)) {
            if (this.state.transactionDoesNotExists) {
                return <p>Page does not exists</p>;
            }
            this.getTransactionData();
        }
        return (
            <Panel header={`Status of a ${this.props.transactionType} Transaction`}
                   bsStyle="default"
                   className="panel-wrapper panel-wrapper-container">
                <Col sm={12} md={9}>
                    <p>ID: {transactionData.transactionId}</p>
                    <p>Current state: <b>{transactionData.state}</b></p>
                    <br/>
                    <b>History of states:</b>
                    <Table responsive striped>
                        <thead>
                            <tr>
                                <th>Timestamp</th>
                                <th>State</th>
                            </tr>
                        </thead>
                        <tbody>
                            {stateHistory.map((state, i) =>{
                                return (
                                    <tr key={i}>
                                        <td>{state.timestamp}</td>
                                        <td>{state.state}</td>
                                    </tr>
                                )
                            })}
                        </tbody>
                    </Table>
                </Col>
            </Panel>
        );
    }

    getTransactionData() {
        let transactionType = this.props.transactionType.toLowerCase();
        if (transactionType === 'withdrawal') {
            transactionType = 'withdraw';
        }
        $.getJSON(
            `/${transactionType}/${this.props.match.params.transactionId}/status-api/`,
        )
          .done(data => { this.setState({transactionData: data}); })
          .fail(() => { this.setState({transactionDoesNotExists: true}); });
    }
}
