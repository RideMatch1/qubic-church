/**
 * Documentation configuration for the Bitcoin-Qubic Bridge Research
 * Structured following IMRAD academic format:
 * Introduction, Methods, Results, and Discussion
 */

import type { DocsConfig } from '@/lib/opendocs/types/docs'

export const docsConfig: DocsConfig = {
  mainNav: [
    {
      href: '/docs',

      title: {
        en: 'Research',
        pt: 'Pesquisa',
      },
    },
  ],

  sidebarNav: [
    {
      title: {
        en: 'Introduction',
        pt: 'Introducao',
      },

      items: [
        {
          href: '/docs',

          title: {
            en: 'Overview',
            pt: 'Visao Geral',
          },

          items: [],
        },

        {
          href: '/docs/01-introduction/02-background',

          title: {
            en: 'Background',
            pt: 'Contexto',
          },

          items: [],
        },

        {
          href: '/docs/01-introduction/03-motivation',

          title: {
            en: 'Motivation',
            pt: 'Motivacao',
          },

          items: [],
        },

        {
          href: '/docs/01-introduction/04-objectives',

          title: {
            en: 'Objectives',
            pt: 'Objetivos',
          },

          items: [],
        },
      ],
    },

    {
      title: {
        en: 'Methods',
        pt: 'Metodos',
      },

      items: [
        {
          href: '/docs/02-methods/01-methodology',

          title: {
            en: 'Methodology',
            pt: 'Metodologia',
          },

          items: [],
        },

        {
          href: '/docs/02-methods/02-tools',

          title: {
            en: 'Tools',
            pt: 'Ferramentas',
          },

          items: [],
        },

        {
          href: '/docs/02-methods/03-verification',

          title: {
            en: 'Verification',
            pt: 'Verificacao',
          },

          items: [],
        },

        {
          href: '/docs/02-methods/04-analysis-framework',

          title: {
            en: 'Analysis Framework',
            pt: 'Framework de Analise',
          },

          items: [],
        },

        {
          href: '/docs/02-methods/05-statistical-rigor',

          title: {
            en: 'Statistical Rigor',
            pt: 'Rigor Estatistico',
          },

          items: [],
        },
      ],
    },

    {
      title: {
        en: 'Results',
        pt: 'Resultados',
      },

      items: [
        {
          href: '/docs/03-results/01-bitcoin-bridge',

          title: {
            en: 'The Bitcoin Bridge',
            pt: 'A Ponte Bitcoin',
          },

          items: [],
        },

        {
          href: '/docs/03-results/02-formula-discovery',

          title: {
            en: 'Formula Discovery',
            pt: 'Descoberta da Formula',
          },

          items: [],
        },

        {
          href: '/docs/03-results/03-jinn-architecture',

          title: {
            en: 'JINN Architecture',
            pt: 'Arquitetura JINN',
          },

          items: [],
        },

        {
          href: '/docs/03-results/04-arb-oracle',

          title: {
            en: 'ARB Oracle',
            pt: 'Oraculo ARB',
          },

          items: [],
        },

        {
          href: '/docs/03-results/05-time-lock',

          title: {
            en: 'Time-Lock Mechanism',
            pt: 'Mecanismo Time-Lock',
          },

          items: [],
        },

        {
          href: '/docs/03-results/06-additional-findings',

          title: {
            en: 'Additional Findings',
            pt: 'Descobertas Adicionais',
          },

          items: [],
        },

        {
          href: '/docs/03-results/07-lost-knowledge-recovery',

          title: {
            en: 'Lost Knowledge Recovery',
            pt: 'Recuperacao de Conhecimento',
          },

          items: [],
        },

        {
          href: '/docs/03-results/08-unified-theory',

          title: {
            en: 'The Unified Theory',
            pt: 'A Teoria Unificada',
          },

          items: [],
        },

        {
          href: '/docs/03-results/09-identity-protocols',

          title: {
            en: 'Identity Protocols',
            pt: 'Protocolos de Identidade',
          },

          items: [],
        },

        {
          href: '/docs/03-results/10-paracosm-blueprint',

          title: {
            en: 'Paracosm Blueprint',
            pt: 'Blueprint do Paracosm',
          },

          items: [],
        },

        {
          href: '/docs/03-results/11-timeline-prophecy',

          title: {
            en: 'Timeline Prophecy',
            pt: 'Profecia do Cronograma',
          },

          items: [],
        },

        {
          href: '/docs/03-results/12-discord-summary',

          title: {
            en: 'Discord Summary',
            pt: 'Resumo Discord',
          },

          items: [],
        },

        {
          href: '/docs/03-results/13-mathematical-proofs',

          title: {
            en: 'Mathematical Proofs',
            pt: 'Provas Matematicas',
          },

          items: [],
        },

        {
          href: '/docs/03-results/15-forgotten-evidence',

          title: {
            en: 'Forgotten Evidence',
            pt: 'Evidencias Esquecidas',
          },

          items: [],
        },

        {
          href: '/docs/03-results/16-anna-bot-analysis',

          title: {
            en: 'Anna Bot Oracle Analysis',
            pt: 'Analise do Oraculo Anna',
          },

          items: [],
        },

        {
          href: '/docs/03-results/17-aigarth-architecture',

          title: {
            en: 'Aigarth Architecture',
            pt: 'Arquitetura Aigarth',
          },

          items: [],
        },

        {
          href: '/docs/03-results/18-the-bridge-hypothesis',

          title: {
            en: 'The Bridge Hypothesis',
            pt: 'A Hipótese da Ponte',
          },

          items: [],
        },

        {
          href: '/docs/03-results/19-aigarth-technical-mapping',

          title: {
            en: 'Aigarth Technical Mapping',
            pt: 'Mapeamento Técnico Aigarth',
          },

          items: [],
        },

        {
          href: '/docs/03-results/20-discord-evidence',

          title: {
            en: 'Discord Archaeology',
            pt: 'Arqueologia do Discord',
          },

          items: [],
        },

        {
          href: '/docs/03-results/21-patoshi-forensics',

          title: {
            en: 'Patoshi Forensics',
            pt: 'Análise Forense Patoshi',
          },

          items: [],
        },

        {
          href: '/docs/03-results/22-negative-results',

          title: {
            en: 'Negative Results',
            pt: 'Resultados Negativos',
          },

          items: [],
        },

        {
          href: '/docs/03-results/23-the-qubic-codex',

          title: {
            en: 'The Qubic Codex',
            pt: 'O Codex Qubic',
          },

          items: [],
        },

        {
          href: '/docs/03-results/24-cfb-satoshi-connection',

          title: {
            en: 'CFB = Satoshi: The Evidence',
            pt: 'CFB = Satoshi: A Evidência',
          },

          items: [],
        },

        {
          href: '/docs/03-results/25-anna-oracle-proof',

          title: {
            en: 'Anna Oracle - Mathematical Proof',
            pt: 'Anna Oracle - Prova Matemática',
          },

          items: [],
        },

        {
          href: '/docs/03-results/26-pattern-27-discovery',

          title: {
            en: 'The -27 Pattern Discovery',
            pt: 'Descoberta do Padrão -27',
          },

          items: [],
        },

        {
          href: '/docs/03-results/27-shalecoins-fracking-research',

          title: {
            en: 'Shalecoins & Fracking Research',
            pt: 'Pesquisa de Shalecoins e Fracking',
          },

          items: [],
        },

        {
          href: '/docs/03-results/28-mt576-genesis-connection',

          title: {
            en: 'The MT576-Genesis Connection',
            pt: 'A Conexão MT576-Genesis',
          },

          items: [],
        },

        {
          href: '/docs/03-results/29-numogram-architecture',

          title: {
            en: 'The Numogram Connection',
            pt: 'A Conexão Numogram',
          },

          items: [],
        },

        {
          href: '/docs/03-results/30-genesis-block-connections',

          title: {
            en: 'Genesis Block Analysis',
            pt: 'Análise do Bloco Gênesis',
          },

          items: [],
        },

        {
          href: '/docs/03-results/31-mathematical-bridges',

          title: {
            en: 'Mathematical Bridges',
            pt: 'Pontes Matemáticas',
          },

          items: [],
        },

        {
          href: '/docs/03-results/32-mirror-wallets',

          title: {
            en: 'Mirror Wallets',
            pt: 'Carteiras Espelho',
          },

          items: [],
        },

        {
          href: '/docs/03-results/33-bitcoin-key-generation',

          title: {
            en: 'Bitcoin Key Generation',
            pt: 'Geração de Chaves Bitcoin',
          },

          items: [],
        },

        {
          href: '/docs/03-results/34-pattern-121-discovery',

          title: {
            en: 'The Pattern 121 Discovery',
            pt: 'A Descoberta do Padrão 121',
          },

          items: [],
        },

        {
          href: '/docs/03-results/35-god-mode-discoveries',

          title: {
            en: 'God Mode Discoveries',
            pt: 'Descobertas do Modo Deus',
          },

          items: [],
        },

        {
          href: '/docs/03-results/36-unexplored-frontiers',

          title: {
            en: 'Unexplored Frontiers',
            pt: 'Fronteiras Inexploradas',
          },

          items: [],
        },

        {
          href: '/docs/03-results/37-k12-breakthrough',

          title: {
            en: 'The K12 Breakthrough',
            pt: 'A Descoberta K12',
          },

          items: [],
        },

        {
          href: '/docs/03-results/38-0x7b-family',

          title: {
            en: 'The 0x7b Family',
            pt: 'A Família 0x7b',
          },

          items: [],
        },

        {
          href: '/docs/03-results/39-seed-analysis',

          title: {
            en: 'Seed Analysis',
            pt: 'Análise de Sementes',
          },

          items: [],
        },

        {
          href: '/docs/03-results/40-1cf-census',

          title: {
            en: 'The 1CF Address Census',
            pt: 'O Censo de Endereços 1CF',
          },

          items: [],
        },

        {
          href: '/docs/03-results/41-genesis-seed-testing',

          title: {
            en: 'Genesis Seed Testing',
            pt: 'Teste de Seeds Genesis',
          },

          items: [],
        },

        {
          href: '/docs/03-results/42-21e8-block-mystery',

          title: {
            en: 'The 21e8 Block Mystery',
            pt: 'O Mistério do Bloco 21e8',
          },

          items: [],
        },

        {
          href: '/docs/03-results/43-the-bridge-revelation',

          title: {
            en: 'The Bridge Revelation',
            pt: 'A Revelação da Ponte',
          },

          items: [],
        },

        {
          href: '/docs/03-results/44-blockchain-archaeology',

          title: {
            en: 'Blockchain Archaeology',
            pt: 'Arqueologia Blockchain',
          },

          items: [],
        },

        {
          href: '/docs/03-results/45-mybitcoin-whale-investigation',

          title: {
            en: 'MyBitcoin Whale Investigation',
            pt: 'Investigação da Baleia MyBitcoin',
          },

          items: [],
        },

        {
          href: '/docs/03-results/47-anna-matrix-lexikon',

          title: {
            en: 'Anna Matrix Lexikon',
            pt: 'Léxico da Matrix Anna',
          },

          items: [],
        },

        {
          href: '/docs/03-results/51-anna-matrix-symmetry',

          title: {
            en: 'Point-Symmetry Discovery',
            pt: 'Descoberta de Simetria',
          },

          items: [],
        },

        {
          href: '/docs/03-results/52-68-anomaly-cells',

          title: {
            en: 'The 68 Anomaly Cells',
            pt: 'As 68 Células Anômalas',
          },

          items: [],
        },

        {
          href: '/docs/03-results/53-decode-key-system',

          title: {
            en: 'Decode Key System',
            pt: 'Sistema de Chave Decode',
          },

          items: [],
        },

        {
          href: '/docs/03-results/54-1cfb-solution-breakthrough',

          title: {
            en: '1CFB Solution Breakthrough',
            pt: 'Avanço na Solução 1CFB',
          },

          items: [],
        },

        {
          href: '/docs/03-results/55-fibonacci-encoding',

          title: {
            en: 'Fibonacci Encoding',
            pt: 'Codificação Fibonacci',
          },

          items: [],
        },

        {
          href: '/docs/03-results/56-127-formula-discovery',

          title: {
            en: 'The 127 Formula',
            pt: 'A Fórmula 127',
          },

          items: [],
        },

        {
          href: '/docs/03-results/57-position-encoding',

          title: {
            en: 'Position Encoding',
            pt: 'Codificação de Posição',
          },

          items: [],
        },

        {
          href: '/docs/03-results/58-perfect-powers-geography',

          title: {
            en: 'Perfect Powers Geography',
            pt: 'Geografia de Potências',
          },

          items: [],
        },

        {
          href: '/docs/03-results/59-mersenne-recursion',

          title: {
            en: 'Mersenne Recursion',
            pt: 'Recursão de Mersenne',
          },

          items: [],
        },

        {
          href: '/docs/03-results/60-64-pairs-complete-analysis',

          title: {
            en: '64 Pairs Complete Analysis',
            pt: 'Análise Completa de 64 Pares',
          },

          items: [],
        },

        {
          href: '/docs/03-results/61-hidden-messages-complete',

          title: {
            en: 'Hidden Messages Complete',
            pt: 'Mensagens Ocultas Completa',
          },

          items: [],
        },

        {
          href: '/docs/03-results/62-negative-results-validation',

          title: {
            en: 'Negative Results (Validation)',
            pt: 'Resultados Negativos (Validação)',
          },

          items: [],
        },

        {
          href: '/docs/03-results/63-validation-report-complete',

          title: {
            en: 'Validation Report Complete',
            pt: 'Relatório de Validação Completo',
          },

          items: [],
        },

        {
          href: '/docs/03-results/64-cfb-signature-breakthrough',

          title: {
            en: 'CFB Signature Breakthrough',
            pt: 'Descoberta da Assinatura CFB',
          },

          items: [],
        },

        {
          href: '/docs/03-results/65-validated-message-inventory',

          title: {
            en: 'Validated Message Inventory',
            pt: 'Inventário de Mensagens Validadas',
          },

          items: [],
        },

        {
          href: '/docs/03-results/66-complete-validation-report',

          title: {
            en: 'Complete Validation Report',
            pt: 'Relatório de Validação Completo',
          },

          items: [],
        },

        {
          href: '/docs/03-results/67-god-mode-breakthrough',

          title: {
            en: 'GOD MODE Breakthrough',
            pt: 'Descoberta GOD MODE',
          },

          items: [],
        },

        {
          href: '/docs/03-results/48-god-mode-discoveries',

          title: {
            en: 'GOD MODE Discoveries',
            pt: 'Descobertas GOD MODE',
          },

          items: [],
        },

        {
          href: '/docs/03-results/51-god-mode-discoveries',

          title: {
            en: 'GOD MODE: Ultimate Analysis',
            pt: 'GOD MODE: Análise Completa',
          },

          items: [],
        },

        {
          href: '/docs/03-results/45-live-resonance-tests',

          title: {
            en: 'Live Resonance Tests',
            pt: 'Testes de Ressonância ao Vivo',
          },

          items: [],
        },

        {
          href: '/docs/03-results/46-strategic-node-inventory',

          title: {
            en: 'Strategic Node Inventory',
            pt: 'Inventário de Nós Estratégicos',
          },

          items: [],
        },

        {
          href: '/docs/03-results/67-honest-assessment',

          title: {
            en: 'Honest Assessment (Audit)',
            pt: 'Avaliação Honesta (Auditoria)',
          },

          items: [],
        },

        {
          href: '/docs/03-results/68-deep-verification-results',

          title: {
            en: 'Deep Verification Results',
            pt: 'Resultados de Verificação Profunda',
          },

          items: [],
        },

        {
          href: '/docs/03-results/69-ai-deep-dive-results',

          title: {
            en: 'AI Deep Dive Results',
            pt: 'Resultados do AI Deep Dive',
          },

          items: [],
        },

        {
          href: '/docs/03-results/70-aigarth-source-analysis',

          title: {
            en: 'Aigarth Source Code Analysis',
            pt: 'Análise do Código Fonte Aigarth',
          },

          items: [],
        },

        {
          href: '/docs/03-results/71-aigarth-live-experiments',

          title: {
            en: 'Aigarth Live Experiments',
            pt: 'Experimentos Aigarth ao Vivo',
          },

          items: [],
        },

        {
          href: '/docs/03-results/72-anna-bot-algorithm',

          title: {
            en: 'Anna-Bot Algorithm Verified',
            pt: 'Algoritmo Anna-Bot Verificado',
          },

          items: [],
        },

        {
          href: '/docs/03-results/73-research-roadmap',

          title: {
            en: 'Research Roadmap',
            pt: 'Roteiro de Pesquisa',
          },

          items: [],
        },

        {
          href: '/docs/03-results/74-future-research-roadmap',

          title: {
            en: 'Future Research Plan',
            pt: 'Plano de Pesquisa Futura',
          },

          items: [],
        },

        {
          href: '/docs/03-results/75-bridge-technical-spec',

          title: {
            en: 'Bridge Technical Specification',
            pt: 'Especificacao Tecnica da Ponte',
          },

          items: [],
        },

        {
          href: '/docs/03-results/14-glossary',

          title: {
            en: 'Glossary',
            pt: 'Glossário',
          },

          items: [],
        },
      ],
    },

    {
      title: {
        en: 'Discussion',
        pt: 'Discussao',
      },

      items: [
        {
          href: '/docs/04-discussion/01-implications',

          title: {
            en: 'Implications',
            pt: 'Implicacoes',
          },

          items: [],
        },

        {
          href: '/docs/04-discussion/02-significance',

          title: {
            en: 'Significance',
            pt: 'Significancia',
          },

          items: [],
        },

        {
          href: '/docs/04-discussion/03-limitations',

          title: {
            en: 'Limitations',
            pt: 'Limitacoes',
          },

          items: [],
        },

        {
          href: '/docs/04-discussion/04-future-work',

          title: {
            en: 'Future Work',
            pt: 'Trabalhos Futuros',
          },

          items: [],
        },
      ],
    },

    {
      title: {
        en: 'Appendices',
        pt: 'Apendices',
      },

      items: [
        {
          href: '/docs/05-appendices/01-raw-data',

          title: {
            en: 'Raw Data Tables',
            pt: 'Tabelas de Dados',
          },

          items: [],
        },

        {
          href: '/docs/05-appendices/02-foundation-facts',

          title: {
            en: 'Foundation Facts',
            pt: 'Fatos Fundamentais',
          },

          items: [],
        },

        {
          href: '/docs/05-appendices/02-source-index',

          title: {
            en: 'Source File Index',
            pt: 'Indice de Arquivos',
          },

          items: [],
        },

        {
          href: '/docs/05-appendices/03-scripts',

          title: {
            en: 'Reproduction Scripts',
            pt: 'Scripts de Reproducao',
          },

          items: [],
        },

        {
          href: '/docs/05-appendices/04-discord-archive',

          title: {
            en: 'Discord Message Archive',
            pt: 'Arquivo de Mensagens',
          },

          items: [],
        },
      ],
    },
  ],
} as const
