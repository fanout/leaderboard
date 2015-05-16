/*
 * Magic Move based on https://github.com/ryanflorence/react-magic-move 0.1.0
 * Adapted for React 0.13 by Katsuyuki Ohmuro
 */
(function() {

    var Clones = React.createClass({
        displayName: 'MagicMoveClones',

        childrenWithPositions:function () {
            return React.Children.map(this.props.children, function(child)  {
                var style = this.props.positions[child.key];
                return React.cloneElement(child, { style:style });
            }.bind(this));
        },

        render:function () {
            return (
                React.createElement("div", {className: this.props.className + ' MagicMoveClones'}, 
                    this.childrenWithPositions()
                )
            );
        }
    });

    var MagicMove = React.createClass({

        displayName: 'MagicMove',

        getInitialState:function () {
            return {
                animating: false
            };
        },

        componentDidMount:function () {
            this.makePortal();
            this.renderClonesInitially();
        },

        componentWillUnmount:function () {
            this.portalNode.parent.removeChild(this.portalNode);
        },

        componentWillReceiveProps:function (nextProps) {
            this.startAnimation(nextProps);
        },

        componentDidUpdate:function (prevProps) {
            if (this.state.animating) {
                this.renderClonesToNewPositions(prevProps);
            }
        },

        makePortal:function () {
            this.portalNode = document.createElement('div');
            this.portalNode.style.left = '-9999px';
            this.portalNode.style.position = 'absolute';
            var baseNode;
            if (this.props.portalBaseId) {
                baseNode = document.getElementById(this.props.portalBaseId);
            } else {
                baseNode = document.body;
            }
            baseNode.appendChild(this.portalNode);
        },

        addTransitionEndEvent:function () {
            // if you click RIGHT before the transition is done, the animation jumps,
            // its because the transitionend event fires even though its not quite
            // done, not sure how to hack around it yet.
            this._transitionHandler = callOnNthCall(this.props.children.length, this.finishAnimation);
            this.portalNode.addEventListener('transitionend', this._transitionHandler);
        },

        removeTransitionEndEvent:function () {
            this.portalNode.removeEventListener('transitionend', this._transitionHandler);
        },

        startAnimation:function (nextProps) {
            if (this.state.animating) {
                return;
            }
            this.addTransitionEndEvent();
            var overrides = {
                animating: true,
                positions: this.getPositions()
            };
            this.renderClones(nextProps, overrides, function()  {
                this.setState({ animating: true });
            }.bind(this));
        },

        renderClonesToNewPositions:function (prevProps) {
            var overrides = {
                positions: this.getPositions()
            };
            this.renderClones(prevProps, overrides);
        },

        finishAnimation:function () {
            this.removeTransitionEndEvent();
            this.portalNode.style.position = 'absolute';
            this.setState({ animating: false });
        },

        getPositions:function () {
            var positions = {};
            React.Children.forEach(this.props.children, function(child)  {
                var ref = child.key;
                var node = this.refs[ref].getDOMNode();
                var rect = node.getBoundingClientRect();
                var computedStyle = getComputedStyle(node);
                var marginTop = parseInt(computedStyle.marginTop, 10);
                var marginLeft = parseInt(computedStyle.marginLeft, 10);
                var position = {
                    top: (rect.top - marginTop),
                    left: (rect.left - marginLeft),
                    width: rect.width,
                    height: rect.height,
                    position: 'absolute'
                };
                positions[ref] = position;
            }.bind(this));
            return positions;
        },

        renderClonesInitially:function () {
            var positions = this.getPositions();
            // this.props.positions = this.getPositions();
            React.render(React.createElement(Clones, React.__spread({},  this.props, {positions: positions})), this.portalNode);
        },

        renderClones:function (props, overrides, cb) {
            this.portalNode.style.position = '';
            React.render(React.createElement(Clones, React.__spread({},  props,  overrides)), this.portalNode, cb);
        },

        childrenWithRefs:function () {
            return React.Children.map(this.props.children, function(child)  {
                return React.cloneElement(child, { ref: child.key });
            });
        },

        render:function () {
            var style = { opacity: this.state.animating ? 0 : 1 };
            return (
                React.createElement("div", {className: this.props.className, style: style}, 
                    this.childrenWithRefs()
                )
            );
        }
    });

    function callOnNthCall(n, fn) {
        var calls = 0;
        return function () {
            calls++;
            if (calls === n) {
                calls = 0;
                return fn.apply(this, arguments);
            }
        };
    }

    window.MagicMove = MagicMove;
})();
