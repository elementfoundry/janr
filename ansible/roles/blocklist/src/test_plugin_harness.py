#!/usr/bin/env python3

from plugins.plugin_manager import PluginManager

# -----------------------------
# bootstrap plugins
# -----------------------------

def bootstrap():
    PluginManager.discover("plugins.formats")
    PluginManager.discover("plugins.transformers")

# -----------------------------
# test data
# -----------------------------

SAMPLE_INPUT = """
# comment line
  GOOGLE.COM
doubleclick.net
  Example.org  
"""


# -----------------------------
# format test
# -----------------------------

def test_format():
    print("\n[TEST] format: plaintext")

    cls = PluginManager.format("plaintext")
    plugin = cls()

    records = plugin.mutate(SAMPLE_INPUT)

    print("records:")
    print(records)

    return records


# -----------------------------
# transformer test
# -----------------------------

def test_transformers(records):

    print("\n[TEST] transformers chain")

    chain = [
        PluginManager.transformer("strip_comments")(),
        PluginManager.transformer("trim")(),
        PluginManager.transformer("lowercase")(),
        PluginManager.transformer("hosts_extract_domain")(),
        PluginManager.transformer("finalize_domain")(),
    ]

    output = []

    for record in records:

        value = record

        print(f"\n raw: {value}")

        for t in chain:
            before = value
            value = t.mutate(value)

            print(
                f"  {t.plugin_name}: "
                f"{before!r} -> {value!r}"
            )

            if value is None:
                break

        if value is not None:
            output.append(value)

    print("\nFINAL OUTPUT:")
    print(output)

    return output


# -----------------------------
# plugin registry inspection
# -----------------------------

def dump_plugins():

    print("\n[PLUGINS] registry dump")

    plugins = PluginManager.list_plugins()

    for category, items in plugins.items():
        print(f"\n{category.upper()}")

        for name in items:
            print(f"  - {name}")


# -----------------------------
# main
# -----------------------------

def main():

    bootstrap()
    dump_plugins()

    records = test_format()

    if not records:
        print("No records produced")
        return

    test_transformers(records)


if __name__ == "__main__":
    main()