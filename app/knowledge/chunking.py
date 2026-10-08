# 离线按 Markdown 结构分块，不调用模型或文档服务；分块目标允许被不可拆的完整单元超过。
"""Structure-aware Markdown chunks; no model or document service involved."""

import re

from app.knowledge.types import ChunkDraft


_HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?)|[ \t]*)$")
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_QA = re.compile(r"^\s*(Q|A|问|答)[:：]\s*(.*)$", re.IGNORECASE)
_CLOSERS = '\"\'”’」』）)]}'


class ChunkingError(ValueError):
    """Safe document/section diagnostics without including body contents."""


# 跟踪反引号或波浪线围栏；只接受同字符、长度足够且末尾无文本的关闭行。
def _fence_state(line: str, fence: str | None) -> str | None:
    match = _FENCE.match(line)
    if not match:
        return fence
    run, trailing = match.groups()
    if fence is None:
        return run
    if run[0] == fence[0] and len(run) >= len(fence) and not trailing.strip():
        return None
    return fence


# 在代码围栏外识别 Markdown 标题，按标题层级生成章节路径与不含标题的正文。
def _sections(text: str):
    stack: list[tuple[int, str]] = []
    body: list[str] = []
    fence = None
    for line in text.splitlines():
        heading = _HEADING.match(line) if fence is None else None
        if heading:
            if body:
                yield [title for _, title in stack], "\n".join(body)
                body = []
            level = len(heading[1])
            title = re.sub(r"[ \t]+#+[ \t]*$", "", heading[2] or "").strip()
            # 同级或更高层标题结束原路径，较低层标题继续挂在父章节下。
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, title))
        else:
            body.append(line)
            fence = _fence_state(line, fence)
    if body:
        yield [title for _, title in stack], "\n".join(body)


# 合并一组问题与回答；显式 FAQ 问题必须非空且有回答，普通正文可使用章节标题。
def _qa_group(questions: list[str], answer: list[str], title: str) -> tuple[str, str]:
    if questions and (not all(question.strip() for question in questions) or not any(line.strip() for line in answer)):
        raise ValueError("FAQ group requires nonempty questions and answer")
    return "\n".join(questions) or title, "\n".join(answer)


# 把围栏外的 Q/问、A/答标记组织成问答组；连续问题共享随后回答。
def _qa_groups(body: str, title: str):
    questions: list[str] = []
    answer: list[str] = []
    answering = False
    fence = None
    for line in body.splitlines():
        match = _QA.match(line) if fence is None else None
        if match and match[1].upper() in ("Q", "问"):
            if answering or (not questions and any(s.strip() for s in answer)):
                yield _qa_group(questions, answer, title)
                questions, answer = [], []
                answering = False
            questions.append(match[2].strip())
        elif match and match[1].upper() in ("A", "答") and questions:
            answer.append(match[2])
            answering = True
        else:
            answer.append(line)
            fence = _fence_state(line, fence)
    if questions or any(line.strip() for line in answer):
        yield _qa_group(questions, answer, title)


# 保留标点、闭合引号与空白切出句子，并标明是否遇到完整句末。
def _sentences(text: str) -> list[tuple[str, bool]]:
    """Keep punctuation, closing quotes and whitespace; flag complete sentences."""
    result = []
    start = index = 0
    while index < len(text):
        char = text[index]
        boundary = char in "。?!！？"
        if char == "!" and index > 0 and text[index - 1:index + 11] == "[!IMPORTANT]":
            boundary = False
        # 小数点不分句，英文句点只在结尾、空白或闭合符号前作为句末。
        if char == ".":
            decimal = index > 0 and index + 1 < len(text) and text[index - 1].isdigit() and text[index + 1].isdigit()
            boundary = not decimal and (index + 1 == len(text) or text[index + 1].isspace() or text[index + 1] in _CLOSERS)
        if boundary:
            end = index + 1
            while end < len(text) and (text[end] in _CLOSERS or text[end] in "。?!！？"):
                end += 1
            while end < len(text) and text[end].isspace():
                end += 1
            result.append((text[start:end], True))
            start = end
            index = end
        else:
            index += 1
    if start < len(text):
        result.append((text[start:], False))
    return result


# 从正文末尾取不超过上限的连续完整句；尾部残句不会参与重叠。
def _suffix(text: str, limit: int) -> str:
    result = ""
    for sentence, complete in reversed(_sentences(text)):
        if not complete or len(sentence + result) > limit:
            break
        result = sentence + result
    return result.strip()


# 仅识别代码围栏外的 IMPORTANT 引用标记，用于标记关键条款。
def _important(text: str) -> bool:
    fence = None
    for line in text.splitlines():
        if fence is None and re.match(r"^\s*>\s*\[!IMPORTANT\](?:\s|$)", line):
            return True
        fence = _fence_state(line, fence)
    return False


# 解析 Markdown 表格单元格，忽略转义字符及反引号代码段内的竖线。
def _cells(line: str) -> list[str] | None:
    """Recognize only pipes outside backtick code spans and backslash escapes."""
    cells, start, index, code = [], 0, 0, 0
    while index < len(line):
        char = line[index]
        if char == "\\":
            index += 2
            continue
        if char == "`":
            end = index + 1
            while end < len(line) and line[end] == "`":
                end += 1
            run = end - index
            if not code:
                code = run
            elif run == code:
                code = 0
            index = end
            continue
        if char == "|" and not code:
            cells.append(line[start:index].strip())
            start = index + 1
        index += 1
    if not cells:
        return None
    cells.append(line[start:].strip())
    if not cells[0]:
        cells.pop(0)
    if cells and not cells[-1]:
        cells.pop()
    return cells


# 把章节正文分为段落、代码围栏块和表格，表格返回表头及各数据行。
def _blocks(body: str):
    lines = body.strip().splitlines()
    paragraph: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        fence = _FENCE.match(line)
        header = _cells(line)
        separator = _cells(lines[index + 1]) if index + 1 < len(lines) else None
        table = header and separator and len(header) == len(separator) and all(re.fullmatch(r":?-{3,}:?", c) for c in separator)
        if fence or table or not line.strip():
            if paragraph:
                yield "paragraph", "\n".join(paragraph), []
                paragraph = []
        if fence:
            content = [line]
            state = _fence_state(line, None)
            index += 1
            while index < len(lines):
                content.append(lines[index])
                state = _fence_state(lines[index], state)
                index += 1
                if state is None:
                    break
            yield "code", "\n".join(content), []
            continue
        if table:
            # 分隔行与表头列数必须一致；每个输出块保留原表头和分隔行。
            heading = line + "\n" + lines[index + 1]
            index += 2
            rows = []
            while index < len(lines) and lines[index].strip() and _cells(lines[index]) is not None:
                rows.append(lines[index])
                index += 1
            yield "table", heading, rows
            continue
        if line.strip():
            paragraph.append(line)
        index += 1
    if paragraph:
        yield "paragraph", "\n".join(paragraph), []


# 按目标字符数组合正文块，保留整句和代码块；表格分块时复制表头，正文只重叠完整句。
def _answers(body: str, target: int, overlap: int):
    current = ""
    prose = ""
    for kind, value, rows in _blocks(body):
        if kind == "table":
            if current:
                yield current.strip()
                current = ""
            table = value
            has_row = False
            for row in rows:
                # 每块至少保留一整行，因此过长的单行不会被硬截断。
                if has_row and len(table) + 1 + len(row) > target:
                    yield table
                    table, has_row = value, False
                table += "\n" + row
                has_row = True
            if has_row:
                yield table
            prose = ""
            continue
        # 代码块始终完整；长段落按句切分，单个过长句子仍保持完整。
        units = [(value, False)] if kind == "code" or len(value) <= target else _sentences(value)
        for unit_index, (unit, _) in enumerate(units):
            separator = "\n\n" if unit_index == 0 else ""
            if current and len(current + separator + unit) > target:
                yield current.strip()
                # 重叠只取此前正文的完整句尾，不跨代码块或表格复制上下文。
                suffix = _suffix(prose, overlap) if kind != "code" else ""
                current = suffix if len(suffix + separator + unit) <= target else ""
                prose = current
            current = current + (separator if current else "") + unit
            prose = prose + (separator if prose else "") + unit if kind != "code" else ""
    if current.strip():
        yield current.strip()


# 校验类型与分块参数，把章节或 FAQ 转为知识草稿；空正文及问答错误附带文档、章节定位。
def chunk_markdown(text: str, *, document_name: str, content_type: str,
                   target_chars: int = 1200, overlap_chars: int = 120) -> list[ChunkDraft]:
    if content_type not in {"policy", "faq", "manual"}:
        raise ValueError("content_type must be policy, faq or manual")
    if type(target_chars) is not int or target_chars < 1 or type(overlap_chars) is not int or overlap_chars < 0:
        raise ValueError("chunk sizes must be positive target and nonnegative overlap integers")
    chunks = []
    for path, body in _sections(text):
        path = path or [document_name]
        section_path = "/".join(path)
        try:
            groups = _qa_groups(body, path[-1]) if content_type == "faq" else [(path[-1], body)]
            for questions, answer in groups:
                for part in _answers(answer, target_chars, overlap_chars):
                    # 分类和标题承载问题语境，路径、类型与关键条款标记另外保存在草稿中。
                    chunks.append(ChunkDraft(category="/".join(path[:-1]) or document_name,
                                             questions=questions, answer=part, section_path=section_path,
                                             content_type=content_type,
                                             is_key_clause=_important(part)))
        except ValueError as exc:
            raise ChunkingError(f"文档 {document_name!r} 章节 {section_path!r}: {exc}") from exc
    if not chunks:
        raise ChunkingError(f"文档 {document_name!r}: no nonempty body")
    return chunks
