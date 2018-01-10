import Status from './Status';

export default class DepositStatus extends Status {
    constructor(props) {
        super(props);
        this.state.isDeposit = true;
    }
}
