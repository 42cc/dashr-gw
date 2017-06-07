import React from "react";


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
            pageTempate = <p>Page does not exists</p>;

        if (page !== null) {
            pageTempate = (
                <div dangerouslySetInnerHTML={{__html: page.description}}/>
            )
        }
        return pageTempate;
    }
}
