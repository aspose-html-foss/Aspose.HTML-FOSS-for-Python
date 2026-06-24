"""Adoption Agency Algorithm — §13.2.6.4.7.

Called from the IN_BODY handler for misnested formatting elements.
Mutates tree_builder's open_elements stack, active_formatting list,
and the document tree in place.

The step labels in comments match the spec numbering for auditability.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aspose_html.tokenizer import StartTagToken, EndTagToken
    from aspose_html.tree._builder import TreeBuilder

# §13.2.6.4.7 — formatting elements subject to the AAA
_FORMATTING_ELEMENTS: frozenset[str] = frozenset({
    "a", "b", "big", "code", "em", "font", "i", "nobr",
    "s", "small", "strike", "strong", "tt", "u",
})


def run_adoption_agency_algorithm(
    tree_builder: TreeBuilder,
    token: StartTagToken | EndTagToken,
) -> None:
    """Execute the adoption agency algorithm per §13.2.6.4.7.

    Called from the IN_BODY handler for misnested formatting elements.
    Mutates tree_builder's open_elements stack, active_formatting list,
    and the document tree in place.

    Parameters
    ----------
    tree_builder : TreeBuilder
        The active tree builder instance.
    token : StartTagToken | EndTagToken
        The current token being processed.

    Notes
    -----
    The algorithm is directly transcribed from §13.2.6.4.7. The step
    labels in comments match the spec numbering for auditability.
    """
    subject = token.tag_name  # type: ignore[union-attr]

    # Step 1: Let subject be the tag name of the token.

    # Step 2: If the current node is an HTML element whose tag name is subject,
    # and it is not in the list of active formatting elements, pop it and return.
    current = tree_builder._open_elements.current
    if (
        current is not None
        and current._local_name == subject
        and not tree_builder._active_formatting.contains(current)
    ):
        tree_builder._open_elements.pop()
        return

    # Step 3: Let outer loop counter be 0.
    outer_counter = 0

    # Step 4: Outer loop.
    while True:
        # Step 4.1: If outer loop counter >= 8, return.
        if outer_counter >= 8:
            return

        # Step 4.2: Increment outer loop counter by 1.
        outer_counter += 1

        # Step 4.3: Let formatting element be the last element in the list
        # of active formatting elements that: is between the end of the list
        # and the last marker in the list, if any, and has the tag name subject;
        # or is nowhere in the list if there is no such element.
        formatting_element = None
        for entry in reversed(list(tree_builder._active_formatting)):
            if tree_builder._active_formatting.is_marker(entry):
                break
            if entry._local_name == subject:  # type: ignore[union-attr]
                formatting_element = entry
                break

        # Step 4.4: If there is no such element, return and instead act as
        # described in the "any other end tag" entry above.
        if formatting_element is None:
            _any_other_end_tag(tree_builder, subject)
            return

        # Step 4.5: If formatting element is not in the stack of open elements,
        # remove it from the list, and return.
        if not tree_builder._open_elements.contains_node(formatting_element):
            tree_builder._active_formatting.remove(formatting_element)
            return

        # Step 4.6: If formatting element is in the stack of open elements,
        # but the element is not in scope, return a parse error and return.
        if not tree_builder._open_elements.has_in_scope(subject):
            tree_builder._add_parse_error(
                "adoption-agency-algorithm-outcome",
                token,
                f"Formatting element <{subject}> not in scope.",
            )
            return

        # Step 4.7: If formatting element is not the current node, it is a
        # parse error. (Continue regardless.)
        if tree_builder._open_elements.current is not formatting_element:
            tree_builder._add_parse_error(
                "adoption-agency-algorithm-outcome",
                token,
                f"Formatting element <{subject}> is not the current node.",
            )

        # Step 4.8: Let furthest block be the topmost node in the stack of
        # open elements that is lower in the stack than formatting element,
        # and is an element in the special category.
        fmt_idx = tree_builder._open_elements.index_of(formatting_element)
        furthest_block = None
        furthest_block_idx = -1
        for i in range(fmt_idx + 1, len(tree_builder._open_elements._stack)):
            el = tree_builder._open_elements._stack[i]
            if el._local_name in _SPECIAL_ELEMENTS:
                furthest_block = el
                furthest_block_idx = i

        # Step 4.9: If there is no furthest block, pop all elements from the
        # stack up to and including formatting element, remove formatting element
        # from the active formatting list, and return.
        if furthest_block is None:
            tree_builder._open_elements.pop_until_node(formatting_element)
            tree_builder._active_formatting.remove(formatting_element)
            return

        # Step 4.10: Let common ancestor be the element immediately below
        # formatting element in the stack.
        common_ancestor = tree_builder._open_elements._stack[fmt_idx - 1] if fmt_idx > 0 else None

        # Step 4.11: Let a bookmark note the position of formatting element
        # in the list of active formatting elements relative to the elements
        # on either side of it in the list.
        bookmark_idx = None
        for i, entry in enumerate(tree_builder._active_formatting):
            if entry is formatting_element:
                bookmark_idx = i
                break

        # Step 4.12: Let node and last node be furthest block.
        node = furthest_block
        node_idx = furthest_block_idx
        last_node = furthest_block

        # Step 4.13: Let inner loop counter be 0.
        inner_counter = 0

        # Step 4.14: Inner loop.
        while True:
            # Step 4.14.1: Increment inner loop counter by 1.
            inner_counter += 1

            # Step 4.14.2: Let node be the element immediately above node in
            # the stack of open elements, or if node is no longer in the stack,
            # the element that was immediately above node in the stack when it
            # was last in the stack.
            node_idx -= 1
            if node_idx < 0:
                break
            node = tree_builder._open_elements._stack[node_idx]

            # Step 4.14.3: If node is formatting element, then break.
            if node is formatting_element:
                break

            # Step 4.14.4: If inner loop counter > 3 and node is in the list
            # of active formatting elements, remove node from the list.
            if inner_counter > 3 and tree_builder._active_formatting.contains(node):
                tree_builder._active_formatting.remove(node)

            # Step 4.14.5: If node is not in the list of active formatting
            # elements, remove node from the stack and continue.
            if not tree_builder._active_formatting.contains(node):
                tree_builder._open_elements._stack.pop(node_idx)
                furthest_block_idx -= 1
                continue

            # Step 4.14.6: Create an element for node, in the HTML namespace,
            # with common ancestor as the intended parent.
            new_element = tree_builder._clone_element(node)
            # Replace node in the active formatting list
            tree_builder._active_formatting.replace(node, new_element)
            # Replace node in the open elements stack
            tree_builder._open_elements._stack[node_idx] = new_element
            # Update bookmark if node was at bookmark position
            for i, entry in enumerate(tree_builder._active_formatting):
                if entry is new_element:
                    bookmark_idx = i
                    break
            node = new_element

            # Step 4.14.7: If last node is furthest block, then move the
            # aforementioned bookmark to be immediately after the new node
            # in the list of active formatting elements.
            if last_node is furthest_block:
                for i, entry in enumerate(tree_builder._active_formatting):
                    if entry is new_element:
                        bookmark_idx = i + 1
                        break

            # Step 4.14.8: Append last node to node.
            if last_node._parent is not None:
                last_node._parent.remove_child(last_node)
            node.append_child(last_node)

            # Step 4.14.9: Set last node to node.
            last_node = node

        # Step 4.15: Insert last node into the appropriate place for inserting
        # a node, but using common ancestor as the override target.
        if last_node._parent is not None:
            last_node._parent.remove_child(last_node)

        if common_ancestor is not None:
            loc_parent, loc_before = tree_builder._get_adjusted_insertion_location(
                override_target=common_ancestor
            )
            if loc_before is not None:
                loc_parent.insert_before(last_node, loc_before)
            else:
                loc_parent.append_child(last_node)
        else:
            # Fallback: append to document
            tree_builder._document.append_child(last_node)

        # Step 4.16: Create an element for formatting element, with furthest
        # block as the intended parent.
        new_formatting = tree_builder._clone_element(formatting_element)

        # Step 4.17: Take all the children of furthest block and append them
        # to the element created in step 4.16.
        for child in list(furthest_block._children):
            furthest_block.remove_child(child)
            new_formatting.append_child(child)

        # Step 4.18: Append the new element to furthest block.
        furthest_block.append_child(new_formatting)

        # Step 4.19: Remove formatting element from the list of active
        # formatting elements, and insert the new element into the list of
        # active formatting elements at the position of the aforementioned bookmark.
        tree_builder._active_formatting.remove(formatting_element)
        if bookmark_idx is not None and bookmark_idx <= len(tree_builder._active_formatting._list):
            tree_builder._active_formatting._list.insert(bookmark_idx, new_formatting)
        else:
            tree_builder._active_formatting._list.append(new_formatting)

        # Step 4.20: Remove formatting element from the stack of open elements,
        # and insert the new element into the stack of open elements immediately
        # below the position of furthest block.
        if formatting_element in tree_builder._open_elements._stack:
            tree_builder._open_elements._stack.remove(formatting_element)

        # Find furthest block's new position and insert new_formatting below it
        try:
            fb_idx = tree_builder._open_elements._stack.index(furthest_block)
            tree_builder._open_elements._stack.insert(fb_idx + 1, new_formatting)
        except ValueError:
            tree_builder._open_elements._stack.append(new_formatting)


def _any_other_end_tag(tree_builder: TreeBuilder, tag_name: str) -> None:
    """Handle end tag that is not a formatting element — §13.2.6.4.7 fallback."""
    for i in range(len(tree_builder._open_elements._stack) - 1, -1, -1):
        node = tree_builder._open_elements._stack[i]
        if node._local_name == tag_name:
            # Generate implied end tags (excluding the matching tag)
            _generate_implied_end_tags(tree_builder, exclude=tag_name)
            # Pop down to and including node
            while tree_builder._open_elements._stack:
                el = tree_builder._open_elements._stack.pop()
                if el is node:
                    break
            return
        if node._local_name in _SPECIAL_ELEMENTS:
            # Parse error, ignore end tag
            return


def _generate_implied_end_tags(
    tree_builder: TreeBuilder, exclude: str | None = None
) -> None:
    """Pop implied end tag elements from the stack."""
    _IMPLIED = frozenset({
        "dd", "dt", "li", "optgroup", "option",
        "p", "rb", "rp", "rt", "rtc",
    })
    while tree_builder._open_elements._stack:
        top = tree_builder._open_elements.current
        if top is None:
            break
        if top._local_name == exclude:
            break
        if top._local_name in _IMPLIED:
            tree_builder._open_elements.pop()
        else:
            break


# §13.2.6.4.7 — special elements set
_SPECIAL_ELEMENTS: frozenset[str] = frozenset({
    "address", "applet", "area", "article", "aside", "base", "basefont",
    "bgsound", "blockquote", "body", "br", "button", "caption", "center",
    "col", "colgroup", "dd", "details", "dir", "div", "dl", "dt",
    "embed", "fieldset", "figcaption", "figure", "footer", "form",
    "frame", "frameset", "h1", "h2", "h3", "h4", "h5", "h6", "head",
    "header", "hgroup", "hr", "html", "iframe", "img", "input",
    "isindex", "li", "link", "listing", "main", "marquee", "menu",
    "meta", "nav", "noembed", "noframes", "noscript", "object", "ol",
    "p", "param", "plaintext", "pre", "script", "section", "select",
    "source", "style", "summary", "table", "tbody", "td", "template",
    "textarea", "tfoot", "th", "thead", "title", "tr", "track", "ul",
    "wbr", "xmp",
    # MathML
    "mi", "mo", "mn", "ms", "mtext", "annotation-xml",
    # SVG
    "foreignobject", "desc", "title",
})
